import math
import sys

EPSILON = sys.float_info.epsilon

'''
Given two points, p1 and p2,
an x coordinate, x,
and y coordinates y3 and y4,
compute and return the (x,y) coordinates
of the y intercept of the line segment p1->p2
with the line segment (x,y3)->(x,y4)
'''
def yint(p1, p2, x, y3, y4):
    x1, y1 = p1
    x2, y2 = p2
    x3 = x
    x4 = x
    px = ((x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)) / \
         float((x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4))
    py = ((x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)) / \
         float((x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4))
    return (px, py)


'''
Given three points a,b,c,
computes and returns the area defined by the triangle
a,b,c. 
Note that this area will be negative 
if a,b,c represents a clockwise sequence,
positive if it is counter-clockwise,
and zero if the points are collinear.
'''
def triangleArea(a, b, c):
    return (a[0] * b[1] - a[1] * b[0] + a[1] * c[0] \
            - a[0] * c[1] + b[0] * c[1] - c[0] * b[1]) / 2.0;


'''
Given three points a,b,c,
returns True if and only if 
a,b,c represents a clockwise sequence
(subject to floating-point precision)
'''
def cw(a, b, c):
    return triangleArea(a, b, c) < -EPSILON;


'''
Given three points a,b,c,
returns True if and only if 
a,b,c represents a counter-clockwise sequence
(subject to floating-point precision)
'''
def ccw(a, b, c):
    return triangleArea(a, b, c) > EPSILON;


'''
Given three points a,b,c,
returns True if and only if 
a,b,c are collinear
(subject to floating-point precision)
'''
def collinear(a, b, c):
    return abs(triangleArea(a, b, c)) <= EPSILON


'''
Given a list of points,
sort those points in clockwise order
about their centroid.
Note: this function modifies its argument.
'''
def clockwiseSort(points):
    # get mean x coord, mean y coord
    xavg = sum(p[0] for p in points) / len(points)
    yavg = sum(p[1] for p in points) / len(points)
    angle = lambda p: ((math.atan2(p[1] - yavg, p[0] - xavg) + 2 * math.pi) % (2 * math.pi))
    points.sort(key=angle)


'''
Replace the implementation of computeHull with a correct computation of the convex hull
using the divide-and-conquer algorithm
points is a list of (x,y) values.
So when we return points this will make it draw from point to point in the list
and connect tht least one with the first one
points = [(0,1)] x[0], x[1]
'''
def computeHull(points):
    clockwiseSort(points)

    # Base case because 3 points is a hull
    if len(points) <= 3:
        return points

    # Finds the lowest and highest points to get the mid point with
    highest = max(points, key=lambda point: point[0])
    lowest = min(points, key=lambda point: point[0])

    midpoint = (highest[0] + lowest[0]) / 2

    left_half = []
    right_half = []

    # Splits the points into left and right based off of the mid point
    for i in points:
        if i[0] < midpoint:
            left_half.append(i)
        else:
            right_half.append(i)

    # Recursively calls computeHull
    left_copy = computeHull(left_half)
    right_copy = computeHull(right_half)

    # Calls our merge function
    points = merge(left_copy, right_copy, midpoint)

    # Clockwise sort the points because our splicing was awful
    clockwiseSort(points)
    return points


'''
The merge function takes in the split left and right hull (x, y) list points and the midpoint.
It finds the upper and lower tangents to create the hull and returns th
e points of that hull 
to be merged recursively in computeHull
'''
def merge(left, right, midpoint):
    # Right most point of left hull
    lh_right = max(left, key=lambda point: point[0])
    # Left most point of right hull
    rh_left = min(right, key=lambda point: point[0])

    # Gets the index of the two closest points
    lh_index = left.index(lh_right)
    rh_index = right.index(rh_left)

    # Len of Left and Right
    len_right = len(right)
    len_left = len(left)

    # Right Hull
    uhr_point = right[rh_index]
    lhr_point = right[rh_index]
    # Left Hull
    uhl_point = left[lh_index]
    lhl_point = left[lh_index]

    # Upper yint
    upper_yint = yint(uhr_point, uhl_point, midpoint, 0, sys.maxsize)
    # Lower yint
    lower_yint = yint(lhr_point, lhl_point, midpoint, 0, sys.maxsize)

    while True:
        changed = False

        # Compares the current Y-Int to the next value's Y-Int
        # Upper Hull, Y Int should be lower
        # Check upper right
        # if the following points intercept is greater than the current point and
        # if the current point index is not the length of the list
        if yint(right[(right.index(uhr_point) + 1) % len_right], uhl_point, midpoint, 0, sys.maxsize)[1] <= upper_yint[
            1] and \
                right.index(uhr_point) != ((right.index(uhr_point) + 1) % len_right):
            # checks to see if the next point is below in case the midpoint lies on one of the tests
            if right[(right.index(uhr_point) + 1) % len_right][1] > uhr_point[1]:
                pass
            else:
                uhr_point = right[(right.index(uhr_point) + 1) % len_right]
                upper_yint = yint(uhr_point, uhl_point, midpoint, 0, sys.maxsize)
                changed = True

        # Check upper left
        # if the following points intercept is greater than the current point and
        # if the current point index is not the length of the list
        if yint(uhr_point, left[(left.index(uhl_point) - 1) % len_left], midpoint, 0, sys.maxsize)[1] <= upper_yint[
            1] and \
                left.index(uhl_point) != ((left.index(uhl_point) - 1) % len_left):
            # checks to see if the next point is below in case the midpoint lies on one of the tests
            if left[(left.index(uhl_point) - 1) % len_left][1] > uhl_point[1]:
                pass
            else:
                uhl_point = left[(left.index(uhl_point) - 1) % len_left]
                upper_yint = yint(uhr_point, uhl_point, midpoint, 0, sys.maxsize)
                changed = True

        # Lower Hull, Y Int should be higher
        # Check lower right
        # if the following points intercept is less than the current point and
        # if the current point index is not the length of the list
        if yint(right[(right.index(lhr_point) - 1) % len_right], lhl_point, midpoint, 0, sys.maxsize)[1] >= lower_yint[
            1] and \
                right.index(lhr_point) != ((right.index(lhr_point) - 1) % len_right):
            # checks to see if the next point is above in case the midpoint lies on one of the tests
            if right[(right.index(lhr_point) - 1) % len_right][1] < lhr_point[1]:
                pass
            else:
                lhr_point = right[(right.index(lhr_point) - 1) % len_right]
                lower_yint = yint(lhr_point, lhl_point, midpoint, 0, sys.maxsize)
                changed = True

        # Check lower left
        # if the following points intercept is less than the current point and
        # if the current point index is not the length of the list
        if yint(lhr_point, left[(left.index(lhl_point) + 1) % len_left], midpoint, 0, sys.maxsize)[1] >= lower_yint[
            1] and \
                left.index(lhl_point) != ((left.index(lhl_point) + 1) % len_left):
            # checks to see if the next point is above in case the midpoint lies on one of the tests
            if left[(left.index(lhl_point) + 1) % len_left][1] < lhl_point[1]:
                pass
            else:
                lhl_point = left[(left.index(lhl_point) + 1) % len_left]
                lower_yint = yint(lhr_point, lhl_point, midpoint, 0, sys.maxsize)
                changed = True

        # If not true, we break out of loop because there are no more changes
        if not changed:
            break

    # Outside of loop
    r_right = right[right.index(uhr_point):] + right[:right.index(uhr_point)]
    r_left = left[left.index(lhl_point):] + left[:left.index(lhl_point)]

    # splices the points together
    points = r_right[:r_right.index(lhr_point)]
    points.append(lhr_point)

    points = points + r_left[:r_left.index(uhl_point)]
    points.append(uhl_point)

    # gets rid of duplicates
    points = list(set(points))

    return points
