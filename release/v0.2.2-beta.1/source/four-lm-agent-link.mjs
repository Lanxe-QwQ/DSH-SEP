import { randomUUID } from 'node:crypto';
import { isAbsolute } from 'node:path';
import { pathToFileURL } from 'node:url';

export const name = 'four-lm-agent-link';

/** Optional adapter for an explicitly configured, separately installed 4LM.
 * The external client owns binding validation, policy, backend I/O and recall
 * formatting. This module contains no default installation or user identity.
 */
export async function apply(ctx, config = {}) {
  if (!config.clientModule || !config.bindingFile) return;
  for (const field of ['clientModule', 'bindingFile', 'scopeModule']) {
    if (typeof config[field] !== 'string' || !isAbsolute(config[field])) {
      throw Object.assign(new Error(`4LM requires an absolute local ${field} path.`),
        { code: 'FOUR_LM_CONFIG_PATH_REQUIRED' });
    }
  }
  const { AgentClient, reference } = await import(pathToFileURL(config.clientModule).href);
  const { carrierKeyOf, scopeChainOf } = await import(pathToFileURL(config.scopeModule).href);
  const client = new AgentClient(config.bindingFile);
  ctx.effect(() => () => client.close());
  const captures = new WeakMap();
  const modernScopes = new WeakSet();
  const seen = new WeakMap();

  function capture(session, message, turnId, key) {
    if (message.source?.kind !== 'user') return;
    const text = (message.content || []).filter(block => block.type === 'text')
      .map(block => block.text).join('\n');
    if (!text.trim()) return;
    let messages = seen.get(session);
    if (!messages) {
      messages = new Map();
      seen.set(session, messages);
    }
    const identity = message.id || turnId;
    let pending = messages.get(identity);
    if (!pending) {
      pending = client.processTurn({ sessionId: session.id,
        turnId: message.id ? 'message:' + message.id : turnId, text }).catch(error => {
        if (error.code === 'agent_not_enabled') return { skipped: true };
        throw error;
      });
      messages.set(identity, pending);
      // Event dispatch may precede prompt assembly; the prompt consumer still
      // observes any failure, without an unhandled background rejection.
      pending.catch(() => {});
    }
    if (key) captures.set(key, pending);
    return pending;
  }

  ctx.on('session/event', function (session, event) {
    if (event.type === 'user/message') {
      capture(session, event.data, String(event.seq), carrierKeyOf(this));
    }
  });

  // Native alpha.2 accepts these messages before committing user/message, so
  // capture and recall must already complete for the first model request.
  ctx.on('agent/pre-step', async function ({ agent, signal }, next) {
    const decision = await next();
    if (decision.kind === 'reject' || signal?.aborted) return decision;
    const key = carrierKeyOf(this);
    if (key) modernScopes.add(key);
    const pending = decision.messages
      .map(message => capture(agent.session, message, message.id, key)).filter(Boolean);
    if (!pending.length) return decision;
    const values = await Promise.all(pending);
    signal?.throwIfAborted();
    const value = values.filter(result => !result.skipped).at(-1);
    if (!value) return decision;
    const memory = Object.freeze({
      id: randomUUID(), role: 'user',
      source: Object.freeze({ kind: 'plugin:four-lm-agent-link', name }),
      content: Object.freeze([Object.freeze({ type: 'text', text: reference(value) })]),
    });
    return { ...decision, messages: [...decision.messages, memory] };
  });

  // Preserve the established older-runtime path; scoped modern recall wins.
  ctx.on('system-prompt/assemble', async (assembly, context, next) => {
    assembly = next ? await next() : assembly;
    const chain = scopeChainOf ? scopeChainOf(context.scope) : [context.scope];
    if (chain.some(key => key && modernScopes.has(key))) return assembly;
    const pending = chain.map(key => key && captures.get(key)).find(Boolean);
    if (!pending) return assembly;
    const value = await pending;
    if (value.skipped) return assembly;
    return { ...assembly, contexts: [...assembly.contexts,
      { name: '4lm-memory', text: reference(value) }] };
  });
}
