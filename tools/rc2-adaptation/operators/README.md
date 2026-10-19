# One-shot lab build and verification operators

These are exact captured lab scripts, retained to review the Windows final
archive/document deltas and Linux proof comparison. They deliberately reference
the fixed D: stage generations. Existing outputs are frequently exclusive; do
not execute these as generic installers or assume they are idempotent.

The product entries live in the delivered archive. Runtime adaptation source is
`../candidate`, builders in `../build`, native Linux source in `../linux/runtime`,
and current Mac composition in `../macos`. The 359-file desktop source overlay
must be restored over the exact official RC.2 source input before building.
The source index proves captured bytes only; execution results are separate.
