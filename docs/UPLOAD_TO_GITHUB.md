# Upload this repository

1. Extract `household-preference-lora-github.zip`.
2. Create an empty GitHub repository, for example `household-preference-lora`.
3. Open Add file → Upload files. Drag the CONTENTS of the extracted `household-preference-lora` directory into it, so README.md is at the repository root. Upload the extracted files, not the ZIP as a single blob.
4. Include `.gitignore` (enable viewing hidden files if needed), and commit with `Add LoRA experiment, evaluation evidence and verified adapter`.
5. Open README.md, confirm folder links work, and check that `adapter/adapter_model.safetensors` and `results/final/metrics.json` are present.

The package has fewer than 100 files and no file above GitHub's documented 25 MiB browser-upload limit; Git LFS is not required for this bundle. GitHub Desktop is an alternative if folder drag-and-drop is inconvenient.

Source: https://docs.github.com/en/repositories/working-with-files/managing-files/adding-a-file-to-a-repository

Suggested repository description: Small-model LoRA experiment for structured preference updates, with raw evaluation evidence and verified adapter reload.
