import cv2


def judge_equal_realize(queryImage, trainImage):
    query_gray = cv2.cvtColor(queryImage, cv2.COLOR_BGR2GRAY)
    train_gray = cv2.cvtColor(trainImage, cv2.COLOR_BGR2GRAY)
    # Initiate ORB detector
    orb = cv2.ORB_create()
    # find the keypoints and descriptors with ORB
    kp1, des1 = orb.detectAndCompute(query_gray, None)
    kp2, des2 = orb.detectAndCompute(train_gray, None)

    # create BFMatcher object
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    # Match descriptors.
    matches = bf.match(des1, des2)
    if calc_equal(matches):
        return True
    else:
        return False


def calc_equal(match_sequence, threshold=20, percentage=0.05):
    good_match = 0
    for match in match_sequence:
        if match.distance <= threshold:
            good_match += 1
    if good_match > len(match_sequence) * percentage:
        return True
    else:
        return False


if __name__ == "__main__":
    img_1 = cv2.imread("image_data/image_2.jpg")  # queryImage
    img_2 = cv2.imread("image_data/image_3.jpg")  # trainImage
    print(judge_equal_realize(img_1, img_2))
