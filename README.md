# hydra-hydrate-hydrus
repo to for some [hydrus](https://github.com/hydrusnetwork/hydrus) related stuff i likely use


## links to hydrus related stuff

### hydrus-scripts-and-presets

a collection of downloaders, themes/presets and scripts for hydrus  
https://github.com/CuddleBear92/Hydrus-Presets-and-Scripts

- big and useful downloader collection, that's about the only thing i have checked out for so far

---

### hydownloader, hydownloader-systray

alternative downloader system for hydrus, based on [gallery-dl](https://github.com/mikf/gallery-dl)  
https://gitgud.io/thatfuckingbird/hydownloader (important to read docs)

<details><summary>note</summary>
-    i quite like it using it with the qt app, very powerful thanks to gallery-dl and the , might switch from downloaders to this  
  
the webui is just as good since it's the same ui but i prefer the actual qt application that lives in my system's notification area/systray
</details>

- has a qt app: https://gitgud.io/thatfuckingbird/hydownloader-systray
  - there's a (highly experimental) webui which is the same as the qt app at `<hydownloader-daemon-addres>/webui` (eg: `http://localhost:53211/webui/`)
  - i installed the systray qt app using the [aur](https://aur.archlinux.org/packages/hydownloader-systray-git) (was more comfortable for me; needs `--settings /path/to/settings.ini` set)

- main config stuff in `<hydownloader-db-folder>/...`
  - `/hydownloader-config.json`
  - `/hydownloader-import-jobs.py`
  - `/gallery-dl-user-config.json` ([config doc](https://github.com/mikf/gallery-dl/blob/master/docs/configuration.rst))

- adding extra metadata retrieval in `/gallery-dl-user-config.json` (such as danbooru artist commentary) requires adding support for it to `/hydownloader-import-jobs.py`
  - important for notes: hydrus separates notes into 'name'/header and content/body by checking for first newline character
 
- has compatibility with [hydrus-companion](https://github.com/DraconicDragon/hydra-hydrate-hydrus/edit/main/README.md#hydrus-companion)

---

### hydrus-companion

feature rich and powerful browser extension for hydrus  
https://gitgud.io/prkc/hydrus-companion (chromium and firefox, read instructions)

<details><summary>note</summary>
-    i like it a lot simply for this feature: it shows what media already exists in hydrus with a green border (and similar stuff; red border if its deleted/trashed)  

i don't use the "send this tab to hydrus" features or similar unfortunately, maybe rarely the "send cookies from this site to hydrus" feature however  
this has a lot of settings i haven't explored yet
</details>

- has compatibility with [hydownloader](https://github.com/DraconicDragon/hydra-hydrate-hydrus/edit/main/README.md#hydownloader)

---

### hydrusnao, wd tagger based tagging

i still want to check these out
https://github.com/GoAwayNow/HydrausNao  
https://github.com/Garbevoir/wd-e621-hydrus-tagger (i assume this will be compatible with other wd taggers such as wd eva02 large/cl-tagger or redrocket's jointtagger)

---

### 

## notes

just want to say that the (advanced) feature to enable systray for hydrus has never broken for me neither on linux or windows 10/11  

### linux stuff

environment: 
- linux 6.12.44-2-cachyos-lts (arch-based) [cachyos](https://cachyos.org/) x86_64
- [kde plasma](https://github.com/KDE/plasma-desktop) 6.4.4 / [hyprland](https://github.com/hyprwm/Hyprland) v0.50.1; **wayland**

#### wayland and mpv

despite what the (probably outdated) documentation page says about wayland support not being great, hydrus was running absolutely fine for me in wayland, however:  
hydrus will crash if [mpv](https://github.com/mpv-player/mpv) and/or hydrus are running natively in wayland  
to solve this, the solution for me was to run *both* hydrus and mpv in xwayland instead **and [run hydrus from source](https://hydrusnetwork.github.io/hydrus/running_from_source.html)** as well
- hydrus was run in xwayland using the `QT_QPA_PLATFORM=xcb` environment variable
- my mpv uses this [mpv_xwayland.conf](https://github.com/DraconicDragon/hydra-hydrate-hydrus/blob/main/mpv_xwayland.conf) file however the only important config option should be `gpu-context=x11egl`
  - the config file includes some extra settings which i didn't all test, but was mostly to get close to high-gpu kind of config; i think there's a bug when a video ends and tries to loop, gets glitched, but it's not an annoyance, yet
