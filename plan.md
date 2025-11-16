You basically want a “single-player lab” on the M4 where Claude can write code, you can iterate fast, and the Linux+3090 only gets pinged once things are stable. Sensible, tragically rare behavior.

Here’s the full plan, tuned so Claude (or any LLM) can implement pieces cleanly.

---

## 1. Overall architecture on the Mac

**Goal:** Everything runs locally on the M4 for fast iteration.

Components:

* **ComfyUI Desktop** on Mac

  * Visual node graph to design pipelines
  * Also acts as your image backend (local HTTP server)
* **Claude CLI**

  * Generates configs, prompt variants, eval prompts
  * Can also write code for you
* **Your “lab” repo** (Git)

  * Holds configs, scripts, workflows, Claude prompts
* **Optional local n8n** (later)

  * For orchestration once pipeline logic is solid

You prototype **end-to-end** here. Once happy, you mirror the same structure to the Linux 3090.

---

## 2. Tools to install on Mac (M4)

### 2.1 ComfyUI Desktop (fastest path on Mac)

Use ComfyUI Desktop for Apple Silicon. It:

* Bundles Python + dependencies
* Uses Metal (MPS) under the hood
* Has UI + server mode

Docs + code: ComfyUI Desktop MacOS docs and repo. ([ComfyUI Documentation][1])

That gives you:

* Local UI: `http://localhost:8188`
* Workflows stored as JSON
* Access to Flux + SDXL etc on M-series chips

### 2.2 Claude CLI

Install on Mac, authenticate with your key. You’ll use it for:

* Generating JSON configs
* Evaluating results
* Auto-writing little helper scripts

You already know what you’re doing there.

### 2.3 Python

You’ll want a normal Python 3.11+ install for utility scripts:

* `run_experiments.py`
* `eval_with_claude.py`
* Any glue you want

---

## 3. Image models to use on M4 (with repos / URLs)

You don’t need a zoo of models. You need a **small, fast, predictable set**.

### 3.1 Core base models

1. **Stable Diffusion 1.5 (fast, light, decent for tests)**

   * Repo:
     `https://huggingface.co/runwayml/stable-diffusion-v1-5`
   * Use: quick low-res tests, sanity checks

2. **SDXL base 1.0 (quality)** ([Hugging Face][2])

   * Repo:
     `https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0`
   * Great for realism at 1024×1024, slower on M4 but fine for single images

3. **SDXL Lightning (speed-optimized SDXL)** ([Hugging Face][3])

   * Repo:
     `https://huggingface.co/ByteDance/SDXL-Lightning`
   * Use for very fast iterations at SDXL-level quality

4. **FLUX.1 [schnell] (modern, fast-ish)** ([Hugging Face][4])

   * Model card:
     `https://huggingface.co/black-forest-labs/FLUX.1-schnell`
   * Inference repo:
     `https://github.com/black-forest-labs/flux`
   * Strong prompt adherence, good general quality

5. **FLUX.1 [dev] (higher quality, heavier)** ([Hugging Face][5])

   * Model card:
     `https://huggingface.co/black-forest-labs/FLUX.1-dev`
   * Use when you care more about quality than speed

Start with:

* **SD 1.5** for fastest rough tests
* **SDXL Lightning** for “realistic enough but quick”
* **Flux.1 schnell** when you want modern behavior with reasonable speed

Then only pull in SDXL base and Flux dev when the pipeline logic is already proven.

---

## 4. Project structure on the Mac

Make something like:

```text
~/dev/ai-lab/
  docker/                # For later, when mirroring to Linux
  configs/
    schema.json
    base_prompt.json
    exp001_params.json
    stages/
      pose.json
      anatomy.json
      lighting.json
      detail.json
  experiments/
    exp001/
      config.json
      notes.md
    exp002/
      config.json
  scripts/
    run_experiments.py
    eval_with_claude.py
  claude/
    prompts/
      generate_params.md
      evaluate_images.md
  workflows/
    comfy/
      pose_pipeline.json
      full_pipeline.json
    n8n/                 # later, when you export flows
  results_dev/
    exp001/
    exp002/
```

Claude can happily generate code that reads/writes this structure.

---

## 5. Backend interface spec (so Claude can code to it)

Even if you stick to ComfyUI, define a **clean API contract** so any backend (Mac or Linux) can implement it.

### 5.1 Single `POST /generate` endpoint

Contract:

* URL: `http://localhost:8188/api/generate` (or your wrapper, see below)
* Method: `POST`
* Request body (JSON):

```json
{
  "experiment_id": "exp001",
  "stage": "pose", 
  "prompt": "full-body portrait, neutral pose, gray background, realistic lighting",
  "negative_prompt": "blurry, distorted, extra limbs, bad anatomy",
  "seed": 123456,
  "width": 768,
  "height": 512,
  "steps": 20,
  "cfg_scale": 6.5,
  "model": "sdxl_lightning",
  "extra": {
    "denoise": 0.35,
    "scheduler": "euler_a"
  }
}
```

* Response body (JSON):

```json
{
  "ok": true,
  "experiment_id": "exp001",
  "stage": "pose",
  "image_path": "results_dev/exp001/pose_001.png",
  "metadata": {
    "seed": 123456,
    "model": "sdxl_lightning",
    "steps": 20,
    "cfg_scale": 6.5,
    "width": 768,
    "height": 512,
    "denoise": 0.35
  }
}
```

You can tell Claude:

> “Implement a FastAPI server that exposes this endpoint and internally calls ComfyUI or diffusers with these fields.”

That’s enough for both scripts and n8n later.

### 5.2 Where ComfyUI fits

You have two options:

1. **Direct ComfyUI API calls**

   * Use ComfyUI’s `/prompt` API with a saved workflow JSON
   * Your scripts construct the `prompt` payload pointing to your workflow
   * No extra server, just ComfyUI itself

2. **Thin wrapper server (recommended for Claude)**

   * Build a small FastAPI service that:

     * Accepts the clean JSON above
     * Translates it into a ComfyUI `/prompt` payload
     * Saves the output image into `results_dev/`
   * Claude can generate this translation layer easily if you show it a sample ComfyUI workflow JSON.

If your goal is “Claude codes it properly,” option 2 is cleaner: one stable contract, backends can change behind it.

---

## 6. UI instructions (ComfyUI on Mac)

You don’t need to overcomplicate the front end. Use ComfyUI itself as your “pipeline UI”.

### 6.1 Basic ComfyUI setup

1. Install ComfyUI Desktop for Mac (Apple Silicon). ([ComfyUI Documentation][1])
2. Launch it, open the browser UI.
3. Install the models:

   * Put SD 1.5 / SDXL / Flux safetensors into the ComfyUI `models` folders as per docs.
4. In settings:

   * Ensure **MPS / Apple GPU** is enabled
   * Use tips for Apple Silicon to avoid running out of memory: lower batch size, smaller resolution, fewer steps. ([Reddit][6])

### 6.2 Build one minimal “base pipeline” graph

In ComfyUI:

* Text node for `prompt`
* Text node for `negative_prompt`
* Model loader node (SD 1.5 or SDXL Lightning first)
* Sampler node
* VAE decode
* Save image node

Save that workflow as:

* `workflows/comfy/pose_pipeline.json`

Then:

* Clone it, add slight modifications for:

  * anatomy pass (maybe img2img with low denoise)
  * lighting pass (adjust prompt, denoise)
* Save as `full_pipeline.json`.

Claude can then:

* Edit those workflow JSONs
* Generate ComfyUI API calls for them
* Wrap them in the FastAPI backend

---

## 7. Scripts for fast iteration

Give Claude these specs so it can write scripts you can actually use.

### 7.1 `scripts/run_experiments.py`

Behavior:

1. Input args:

   * `--config configs/exp001_params.json`
   * `--out results_dev/exp001`
2. Load JSON: a list of experiment objects matching the request schema above
3. For each:

   * Call `POST /generate`
   * Save images and metadata under `results_dev/exp001`
4. Print a summary table (which seeds, which stages, which files)

### 7.2 `scripts/eval_with_claude.py`

Behavior:

1. Input args:

   * `--images results_dev/exp001`
   * `--out results_dev/exp001_eval.json`
2. For each image:

   * Collect basic metadata (filename, stage, seed)
   * Build a prompt for Claude using `claude/prompts/evaluate_images.md`
3. Use Claude CLI to send batched descriptions or thumbnails
4. Save evaluation result as JSON like:

```json
[
  {
    "file": "pose_001.png",
    "pose": 8,
    "anatomy": 7,
    "lighting": 6,
    "realism": 7,
    "notes": "hands slightly distorted, otherwise solid"
  }
]
```

Then later you can ask Claude to turn that into CSV or select top N configs.

---

## 8. Step-by-step: how you actually start on the Mac

1. **Create repo** `~/dev/ai-lab` with the structure above.
2. **Install ComfyUI Desktop**, verify you can generate a simple SD 1.5 image.
3. **Download models**:

   * SD 1.5
   * SDXL base
   * SDXL Lightning
   * Flux.1 schnell
     Place them where ComfyUI expects.
4. **Create minimal ComfyUI workflow** and save as `pose_pipeline.json`.
5. **Ask Claude to**:

   * Generate `configs/schema.json` for experiment configs
   * Write `scripts/run_experiments.py` that:

     * Reads config JSON
     * Calls a mock `/generate` endpoint
6. **Write a mock backend** first (no GPU), responds with a static PNG.
   Check that `run_experiments.py` and the schema all behave.
7. Swap mock backend for a real ComfyUI-backed implementation:

   * Either direct ComfyUI API calls
   * Or a small FastAPI wrapper Claude generates
8. Confirm end-to-end:

   * Run 3–5 experiments
   * Verify images land in `results_dev/exp001`
9. Add `eval_with_claude.py`, plug Claude CLI in the loop.
10. Once all that is stable, you can start worrying about the Linux+3090 clone.

---

You now have:

* Clear models to use, with repos
* A clean API spec
* Folder layout
* UI role (ComfyUI)
* Backend expectations

You can hand any piece of this to Claude and say “implement X according to this spec” and, for once, the poor model will not have to guess what you meant.

[1]: https://docs.comfy.org/installation/desktop/macos?utm_source=chatgpt.com "MacOS Desktop Version"
[2]: https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0?utm_source=chatgpt.com "stabilityai/stable-diffusion-xl-base-1.0"
[3]: https://huggingface.co/collections/SyntheticIAI/stable-diffusion-xl-base-10?utm_source=chatgpt.com "stable-diffusion-xl-base-1.0 - a SyntheticIAI Collection"
[4]: https://huggingface.co/black-forest-labs/FLUX.1-schnell?utm_source=chatgpt.com "black-forest-labs/FLUX.1-schnell"
[5]: https://huggingface.co/black-forest-labs/FLUX.1-dev?utm_source=chatgpt.com "black-forest-labs/FLUX.1-dev"
[6]: https://www.reddit.com/r/comfyui/comments/1lviejb/tips_for_mac_users_on_apple_silicon_especially/?utm_source=chatgpt.com "Tips for Mac users on Apple Silicon (especially for lower- ..."
