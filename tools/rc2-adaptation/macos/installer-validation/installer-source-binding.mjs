// This explicit manifest fixes the unchanged production sources independently
// of the later payload/installer artifact pins. No directory discovery.
import {readFile} from 'node:fs/promises';import {join} from 'node:path';
import {fileBytes,hash} from './installer-binding.mjs';
export const SOURCE_MANIFEST_SHA256='0d20ff00bf69bf127551d77752d1f97ee1e271845fad8cb5613e052cf9dc9067';
export async function verifyInstallerSources(root){
 const bytes=await readFile(new URL('./installer-sources.json',import.meta.url));
 if(hash(bytes)!==SOURCE_MANIFEST_SHA256)throw Object.assign(Error('SEP_NATIVE_INSTALLER_SOURCE_MANIFEST'),{code:'SEP_NATIVE_INSTALLER_SOURCE_MANIFEST'});
 const manifest=JSON.parse(bytes),files=[];
 for(const row of manifest.files){const actual=await fileBytes(join(root,row.path),4194304);if(actual.length!==row.bytes||hash(actual)!==row.sha256)throw Object.assign(Error('SEP_NATIVE_INSTALLER_SOURCE_CHANGED'),{code:'SEP_NATIVE_INSTALLER_SOURCE_CHANGED'});files.push({...row});}
 return {manifestSha256:SOURCE_MANIFEST_SHA256,files};
}