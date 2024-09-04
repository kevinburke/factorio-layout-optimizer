def test_connection_point_logic():
            starts_x, starts_y, pos_bools_start = get_connection_point(model, name1, 'start', pos1, x1, y1, w1, h1, no_rotation1, rotated1)
        ends_x, ends_y, ends_pos_bools = get_connection_point(model, name2, 'end', pos2, x2, y2, w2, h2, no_rotation2, rotated2)
        pos_bools.extend(pos_bools_start)
        pos_bools.extend(ends_pos_bools)

        start_indices = range(len(starts_x))
        end_indices = range(len(ends_x))

        for (start_index, start_x, start_y), (end_index, end_x, end_y) in product(
                zip(start_indices, starts_x, starts_y),
                zip(end_indices, ends_x, ends_y)
            ):
