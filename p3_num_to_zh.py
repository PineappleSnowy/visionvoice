def num_to_zh(num: str | int) -> str:
    """
    :param num: 传入数字的范围须为[0, 99999]，可为字符串或整型
    :return: 数字对应的汉字
    """
    # 处理错误情况
    try:
        int_num = int(num)
        if int_num > 99999 or int_num < 0:
            return "Error: Input num is out of range."
        str_num = str(num)
        if str_num[0] == "0":
            return "Error: Zero occupies the first digit."
    except Exception as e:
        return str(e)
    zh_num = ""
    num_dict = {"0": "零", "1": "一", "2": "二", "3": "三", "4": "四",
                "5": "五", "6": "六", "7": "七", "8": "八", "9": "九"}
    digit_dict = {2: "十", 3: "百", 4: "千", 5: "万"}
    # 处理10+的情况
    if len(str(num)) == 2 and str(num)[0] == "1" and str(num)[1] != "0":
        zh_num += (digit_dict[2] + num_dict[str(num)[1]])
    # 处理10的情况
    elif len(str(num)) == 2 and str(num)[0] == "1" and str(num)[1] == "0":
        zh_num += (digit_dict[2])
    # 处理0的情况
    elif str(num) == "0":
        zh_num += num_dict["0"]
    else:
        # 数字内部（除尾部）是否有0的判断标志
        zero_inside = False
        # digit表示数位
        for i, digit in zip(str(num), range(len(str(num)) + 1)[-1:0:-1]):
            if i == "0":
                zero_inside = True
                continue
            if zero_inside:
                # 数字内部连续的0都用一个零来表示
                zh_num += num_dict["0"]
                zero_inside = False
            # 数位大于等于2时处理数字从某一位开始都是0的情况
            if digit >= 2:
                const_zero = True
                # 从当前下标（当前下标必然非零）的后一位开始遍历
                for j in str(num)[len(str(num)) - digit + 1::]:
                    if j == "0":
                        pass
                    else:
                        const_zero = False
                        break
                if const_zero:
                    zh_num += (num_dict[i] + digit_dict[digit])
                    break
            # 处理个位数字
            if digit == 1:
                zh_num += num_dict[i]
            # 处理一般情况
            else:
                zh_num += (num_dict[i] + digit_dict[digit])
    return zh_num


if __name__ == "__main__":
    print(num_to_zh("90010"))
