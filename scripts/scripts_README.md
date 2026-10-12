# Scripts

The builder validates input and produces the local HTML. The validator enforces repository defaults, not live platform policies. The first-frame helper uses FFmpeg/FFprobe. The handoff builder writes JSON only. Regression tests run offline by default; RUN_YIJIANFA_INTEGRATION=1 explicitly enables optional installed-CLI prepare checks. make_demo.py creates synthetic media and builds an example workbench.
