#include <stdlib.h>
#include <zephyr/kernel.h>
#include "animation.h"

LV_IMG_DECLARE(peripheral_art_00);
LV_IMG_DECLARE(peripheral_art_01);
LV_IMG_DECLARE(peripheral_art_02);
LV_IMG_DECLARE(peripheral_art_03);
LV_IMG_DECLARE(peripheral_art_04);
LV_IMG_DECLARE(peripheral_art_05);

const lv_img_dsc_t *anim_imgs[] = {
    &peripheral_art_00, &peripheral_art_01, &peripheral_art_02,
    &peripheral_art_03, &peripheral_art_04, &peripheral_art_05,
};

#define ANIM_FRAME_COUNT (sizeof(anim_imgs) / sizeof(anim_imgs[0]))

void draw_animation(lv_obj_t *canvas) {
#if IS_ENABLED(CONFIG_NICE_VIEW_GEM_ANIMATION)
    lv_obj_t *art = lv_animimg_create(canvas);
    lv_obj_center(art);

    lv_animimg_set_src(art, (const void **)anim_imgs, ANIM_FRAME_COUNT);
    lv_animimg_set_duration(art, CONFIG_NICE_VIEW_GEM_ANIMATION_MS);
    lv_animimg_set_repeat_count(art, LV_ANIM_REPEAT_INFINITE);
    lv_animimg_start(art);
#else
    lv_obj_t *art = lv_img_create(canvas);

    int length = ANIM_FRAME_COUNT;
    srand(k_uptime_get_32());
    int random_index = rand() % length;
    int configured_index = (CONFIG_NICE_VIEW_GEM_ANIMATION_FRAME - 1) % length;
    int anim_imgs_index = CONFIG_NICE_VIEW_GEM_ANIMATION_FRAME > 0 ? configured_index : random_index;

    lv_img_set_src(art, anim_imgs[anim_imgs_index]);
#endif

    lv_obj_align(art, LV_ALIGN_TOP_LEFT, 36, 0);
}
