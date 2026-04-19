extends SceneTree
# Scratch probe; intentionally inert. Used while diagnosing the preload-hang
# around main.gd; superseded by test_death_cam.gd once the pure-math helpers
# were extracted to DeathCamMath (scripts/death_cam_math.gd). Kept as a
# minimal SceneTree because the Cowork workspace blocks deletion.

func _init() -> void:
	quit(0)
