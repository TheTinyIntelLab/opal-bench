# Rolling prospective evaluation

An entry can score on a screen only if its freeze predates the first public release of that screen's pair outcomes. Check the preprint, supplements and repository deposits as well as the paper. If the release has a date but no time, or you can't establish which happened first, accept the screen only if its release date is later than the freeze date in UTC. Exclude screens the submitter already accessed, along with duplicates and reissues of older outcome tables.

## Record the entry and the screen

A maintainer publishes the accepted entry in a public, append-only registry. Use the UTC time of that publication as the freeze time. Record the submission ID, adapter commit, hashes of weights and other inputs, dependency lock or container digest, training data and cutoff, random seeds, tracks and calibration budgets. A change to the entry gets a new freeze time and can score only on later releases.

For each screen, record the screen ID, source URL, evidence for the earliest public release date, normalization, evaluation units, license and input checksums. Admit screens with a verifiable release date and derived tables that can be redistributed. Apply the benchmark's growth-screen quality and duplicate checks before scoring.

## Score and publish the result

1. **Publish the scoring setup.** Record the screen, metric revision, calibration budgets, number of draws and seed rule before running entries. Use the benchmark's few-shot calibration and metrics. Give each eligible entry the same inputs and draws.
2. **Run the frozen adapter.** Start from its frozen snapshot on each screen. Give the adapter only the singles and the labeled calibration pairs assigned to its budget. Keep the other outcomes with the scorer and run inference without network access to the released labels. Discard any state learned during inference before moving to the next screen.
3. **Append the score.** Key each result by submission ID, screen ID, budget and scoring revision. Record the scoring date, number of evaluated units and any budget the entry skipped. Keep earlier rows and link corrections. Compare methods on the same screens, or list the screens behind an aggregate.

The GitHub Action scores the shipped screens. The prospective board gets its first row when an accepted entry has a later eligible screen to score.
