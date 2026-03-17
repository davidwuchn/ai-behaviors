# #split — Split
Decompose N disjoint domain changes in the working copy into N commits.

split ∩ {ExecuteWithoutConfirmation} = ∅    -- HARD CONSTRAINT
Run `jj diff`. If empty or only one domain group: tell the user and stop.
Group by domain concern — not by file. One group = one coherent why.
Propose: commit message (one line; why, not how) + file list per group. Wait for confirmation.
On confirmation: N-1 × `jj split --files <files>` front-to-back; set message per group.
Intra-file conflicts: assign to dominant domain; note the overlap to the user.
