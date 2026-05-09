#include <zephyr/kernel.h>
#include "art.h"

LV_IMG_DECLARE(layer_art_0);
LV_IMG_DECLARE(layer_art_1);
LV_IMG_DECLARE(layer_art_2);
LV_IMG_DECLARE(layer_art_3);
LV_IMG_DECLARE(layer_art_default);

static const lv_img_dsc_t *layer_art_imgs[] = {
    &layer_art_0,
    &layer_art_1,
    &layer_art_2,
    &layer_art_3,
};

#define LAYER_ART_COUNT (sizeof(layer_art_imgs) / sizeof(layer_art_imgs[0]))

void draw_art_status(lv_obj_t *canvas, const struct status_state *state) {
    const lv_img_dsc_t *art = &layer_art_default;

    if (state->layer_index < LAYER_ART_COUNT) {
        art = layer_art_imgs[state->layer_index];
    }

    lv_draw_image_dsc_t img_dsc;
    lv_draw_image_dsc_init(&img_dsc);
    canvas_draw_img(canvas, 0, 0, art, &img_dsc);

    // Connection overlay: small indicator in top-right corner
    lv_draw_rect_dsc_t rect_dsc;
    init_rect_dsc(&rect_dsc, LVGL_FOREGROUND);

    bool connected = false;
#if defined(CONFIG_ZMK_BLE)
    connected = state->active_profile_connected;
#endif

    if (connected) {
        // Solid dot when connected (creature is "awake")
        canvas_draw_rect(canvas, 58, 2, 6, 6, &rect_dsc);
    } else {
        // Small X when disconnected
        lv_point_t x_points_1[2] = {{58, 2}, {64, 8}};
        lv_point_t x_points_2[2] = {{64, 2}, {58, 8}};
        lv_draw_line_dsc_t line_dsc;
        init_line_dsc(&line_dsc, LVGL_FOREGROUND, 2);
        canvas_draw_line(canvas, x_points_1, 2, &line_dsc);
        canvas_draw_line(canvas, x_points_2, 2, &line_dsc);
    }

    // Low battery overlay: small warning triangle in bottom-right corner
    if (state->battery < 20 && !state->charging) {
        lv_point_t tri_points[4] = {
            {60, 56},
            {64, 64},
            {56, 64},
            {60, 56},
        };
        lv_draw_line_dsc_t line_dsc;
        init_line_dsc(&line_dsc, LVGL_FOREGROUND, 1);
        canvas_draw_line(canvas, tri_points, 4, &line_dsc);
    }
}
