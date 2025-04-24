# Art Capstone

## Generation
Workflow

### Environment
- **WebUI**: ComfyUI (RunPod template: ComfyUI without Flux.1 dev one-click)
- **GPU**: NVIDIA RTX A6000 48 GB
- **Model**: `stable-diffusion-xl-base-1.0` (6.5 GB)
- **No LoRAs or extra KSamplers**

![2.png](screenshots%2F2.png)

![1.png](screenshots%2F1.png)

![3.png](screenshots%2F3.png)

![4.png](screenshots%2F4.png)

Only v1-5-pruned-enaonly-fp16 checkpoint was in the list, so I downloaded sd_xl_base_1.0 manually

![5.png](screenshots%2F5.png)

Verifing

![6.png](screenshots%2F6.png)

### Base KSampler
| Steps | CFG  | Sampler        | Width x Height   |
|-------|------|----------------|------------------|
| 30–50 | 8–10 | `dpmpp_2m_sde` | 1024 x 1024/1536 |

### Album Cover

#### Name of the Work
Thriller studio album by Michael Jackson

#### Original Work

![thriller.png](images%2Falbum%2Foriginal%2Fthriller.png)

#### Positive Prompt
Michael Jackson 1983 Thriller video, zombie makeup and glowing yellow eyes, iconic red leather jacket with black V-panels, torn sleeves, walking forward down a fog-filled midnight street, blue back-light halo, cinematic 35 mm film grain, gritty neon haze, dramatic low-angle shot, high-detail hyper-realism, horror–music-video style, album-cover composition, 8-K studio quality

#### Negative Prompt
duplicate person, extra heads, extra limbs, two MJs, crowded background, gore, mutilation, disfigured hands, low-res, out-of-focus, motion blur, cartoon, pastel, text, watermark, logo

#### Pipeline
![7.png](screenshots%2F7.png)

#### Selected Results

![1.png](images%2Falbum%2Fnew%2F1.png)

![2.png](images%2Falbum%2Fnew%2F2.png)

### Book Cover

#### Name of the Work

Nineteen Eighty-Four (1984) dystopian novel by George Orwell

#### Original Work

![1984.jpg](images%2Fbook%2Foriginal%2F1984.jpg)

#### Positive Prompt

(((1 9 8 4))), (((1 9 8 4))), “1984”, large bold crimson digits, centred,
sleek modern CCTV surveillance camera in sharp focus above the title,
distressed parchment background with faded sepia newsprint and soft coffee-stain rings,
retro-meets-futurist book-cover aesthetic, portrait orientation, high-contrast,
limited palette (deep red, charcoal, warm beige), 8-K print-ready sharpness

#### Negative Prompt

1894, 1994, wrong numbers, duplicate digits, unreadable text, warped letters,
extra text, pastel colours, neon rainbow, cartoon, anime, low-resolution,
watermark, logo, motion blur, cluttered background

#### Pipeline

![8.png](screenshots%2F8.png)

#### Selected Result

![1.png](images%2Fbook%2Fnew%2F1.png)

### Movie Cover

#### Name of the Work

Titanic disaster film by James Cameron

#### Original Work

![titanic.png](images%2Fmovie%2Foriginal%2Ftitanic.png)

#### Positive Prompt

Jack and Rose, elegant Edwardian evening wear, slow-dancing together in the lavish first-class restaurant of the RMS Titanic, richly carved mahogany paneling, crystal chandeliers casting warm golden light, polished parquet floor, white-linen tables with silverware pushed aside, soft string-quartet ambience suggested by blurred musicians in background, gentle reflections on gleaming brass and glass, romantic 1912 atmosphere, 8-K hyper-realism, cinematic wide shot, portrait orientation

#### Negative Prompt

text, title, watermark, duplicate couple, extra people crowding foreground, wrong era clothing, cartoon, pastel, neon, distorted faces, low-resolution, motion blur, logo, noisy background

#### Pipeline

![9.png](screenshots%2F9.png)

#### Selected Result

![1.png](images%2Fmovie%2Fnew%2F1.png)

#### Another Positive Prompt

(((T I T A N I C))), (((T I T A N I C))), “TITANIC”, huge distressed block lettering centred at top,
RMS Titanic bow-first sinking into icy black North Atlantic, stern rising high above churning waves,
cold moonlight and emergency flares illuminating hull, lifeboats rowing away in foreground,
jagged icebergs and storm clouds, cinematic high-drama night scene, 8-K hyper-realism,
portrait-orientation movie poster, rich blue-teal palette with rust-orange firelight

#### Another Negative Prompt

wrong title, TITONIC, TITAN, unreadable letters, duplicate text, cartoon, pastel, neon rainbow,
extra ships, daytime, clear weather, low-resolution, motion blur, watermark, logo, text warp,
crowded foreground, distorted perspective

#### Another Pipeline

![10.png](screenshots%2F10.png)

#### Another Result

![2.png](images%2Fmovie%2Fnew%2F2.png)