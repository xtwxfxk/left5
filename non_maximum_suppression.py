# import the necessary packages
import numpy as np


# Malisiewicz et al.
def non_max_suppression_fast(boxes, overlapThresh):
    # if there are no boxes, return an empty list
    if len(boxes) == 0:
        return []

    # if the bounding boxes integers, convert them to floats --
    # this is important since we'll be doing a bunch of divisions
    if boxes.dtype.kind == "i":
        boxes = boxes.astype("float")

    # initialize the list of picked indexes
    pick = []

    # grab the coordinates of the bounding boxes
    x1 = boxes[:, 0]
    y1 = boxes[:, 1]
    x2 = boxes[:, 2]
    y2 = boxes[:, 3]

    # compute the area of the bounding boxes and sort the bounding
    # boxes by the bottom-right y-coordinate of the bounding box
    area = (x2 - x1 + 1) * (y2 - y1 + 1)
    idxs = np.argsort(y2)

    # keep looping while some indexes still remain in the indexes
    # list
    while len(idxs) > 0:
        # grab the last index in the indexes list and add the
        # index value to the list of picked indexes
        # print '*******\n%s\n*******' % idxs
        last = len(idxs) - 1
        i = idxs[last]
        pick.append(i)

        # find the largest (x, y) coordinates for the start of
        # the bounding box and the smallest (x, y) coordinates
        # for the end of the bounding box
        xx1 = np.maximum(x1[i], x1[idxs[:last]])
        yy1 = np.maximum(y1[i], y1[idxs[:last]])
        xx2 = np.minimum(x2[i], x2[idxs[:last]])
        yy2 = np.minimum(y2[i], y2[idxs[:last]])

        # compute the width and height of the bounding box
        w = np.maximum(0, xx2 - xx1 + 1)
        h = np.maximum(0, yy2 - yy1 + 1)

        # compute the ratio of overlap
        overlap = (w * h) / area[idxs[:last]]

        # delete all indexes from the index list that have
        idxs = np.delete(idxs, np.concatenate(([last],
                                               np.where(overlap > overlapThresh)[0])))

    # return only the bounding boxes that were picked using the
    # integer data type
    return boxes[pick].astype("int")


images = [
    ("images/audrey.jpg", np.array([
        (12, 84, 140, 212),
        (24, 84, 152, 212),
        (36, 84, 164, 212),
        (12, 96, 140, 224),
        (24, 96, 152, 224),
        (22, 107, 153, 237),
        (24, 108, 152, 236), ])),
    ("images/bksomels.jpg", np.array([
        (114, 60, 178, 124),
        (120, 60, 184, 124),
        (114, 66, 178, 130)])),
    ("images/gpripe.jpg", np.array([
        (12, 30, 76, 94),
        (12, 36, 76, 100),
        (72, 36, 200, 164),
        (84, 48, 212, 176)]))]

# loop over the images
for (imagePath, boundingBoxes) in images:
    # # load the image and clone it
    # print "[x] %d initial bounding boxes" % (len(boundingBoxes))
    # image = cv2.imread(imagePath)
    # orig = image.copy()
    #
    # # loop over the bounding boxes for each image and draw them
    # for (startX, startY, endX, endY) in boundingBoxes:
    #     cv2.rectangle(orig, (startX, startY), (endX, endY), (0, 0, 255), 2)
    #
    # # perform non-maximum suppression on the bounding boxes
    pick = non_max_suppression_fast(boundingBoxes, 0.3)
    print pick
    print '########################'