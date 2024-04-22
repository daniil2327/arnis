from time import time
import numpy as np
import matplotlib.path as mplPath
from polylabel import polylabel


def floodFill(
    img, px, py, newColor, currentBuilding, minMaxDistX, minMaxDistY, elementType="None"
):
    currentBuilding = np.delete(currentBuilding, 0, axis=0)
    if len(currentBuilding) <= 2 or not (px < minMaxDistY and py < minMaxDistX):
        return img

    building_path = mplPath.Path(currentBuilding)

    centroid = polylabel([currentBuilding.tolist()], with_distance=True)
    px = round(centroid[0][1])
    py = round(centroid[0][0])
    if not building_path.contains_point((py, px)):
        offset = [(0, 5), (0, -5), (5, 0), (-5, 0)]
        for dx, dy in offset:
            if building_path.contains_point((py + dy, px + dx)):
                px += dx
                py += dy
                break
        else:
            return img

    if str(img[px][py][0])[:1] in ["5", "6"]:
        offset = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        for dx, dy in offset:
            if building_path.contains_point((py + dy, px + dx)):
                px += dx
                py += dy
                break
        else:
            return img

    try:
        oldColor = img[px][py][0]
    except Exception:
        return img

    queue = set([(px, py)])
    seen = set()
    tot_rows, tot_cols = img.shape[:2]

    while queue:
        x, y = queue.pop()
        if img[x][y] == newColor:
            continue
        if not building_path.contains_point((y, x)):
            return img
        img[x][y] = newColor
        seen.add((x, y))

        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < tot_rows and 0 <= ny < tot_cols and (nx, ny) not in seen:
                if (
                    img[nx][ny] == oldColor
                    or (elementType == "building" and img[nx][ny][0] // 10 == 1)
                ):
                    queue.add((nx, ny))

        # Timeout нахуй

    return img