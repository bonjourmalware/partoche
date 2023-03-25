from src.const import (
    UTM_Y_AXIS,
    UTM_X_AXIS,
    X_COEFF,
    Y_COEFF,
    TILE_W,
    TILE_H,
    LINES,
)


def utm_zone_to_coordinates(easting, northing, number, letter):
    min_easting = 166000
    max_easting = 834000
    easting_total_range = max_easting - min_easting
    start, end = map_utm_zone_to_term(number, letter)
    zone_total_range = end[0] - start[0]
    zone_slice_relative_size = easting_total_range // zone_total_range
    x_offset = int((easting // zone_slice_relative_size) - 1)
    x = start[0] + x_offset

    if is_northern(letter):
        min_northing = 0  # equator
        max_northing = 9350000  # 84th north parallel
        equator_offset = northing
    else:
        min_northing = 10000000  # 80th south parallel
        max_northing = 1100000  # equator
        equator_offset = min_northing - northing

    northing_total_range = max_northing - min_northing
    hemisphere_height = LINES // 2
    northing_slice_relative_size = northing_total_range // hemisphere_height
    y = hemisphere_height - int(equator_offset / northing_slice_relative_size)

    return x, y


def map_utm_zone_to_term(number, letter):
    start_x = int(UTM_X_AXIS.index(number) * X_COEFF)
    start_y = int(UTM_Y_AXIS.index(letter) * Y_COEFF)
    end_x = start_x + TILE_W // 2 + TILE_H
    end_y = start_y + TILE_H // 2 + TILE_W
    return (start_x, start_y), (end_x, end_y)


def is_northern(letter):
    return UTM_Y_AXIS.index(letter) < len(UTM_Y_AXIS) // 2
