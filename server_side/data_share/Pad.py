class Pad(object):
    """
    This class provides padding to the bytes object.
    """

    @staticmethod
    def pad(data, base=16):
        """
        The function adds padding to data
        :param data: (bytes) data to be padded
        :param base: (int) padding value
        :return: (bytes) padded data
        """
        assert isinstance(data, bytes)
        length = base - (len(data) % base)
        return data + bytes([length]) * length

    @staticmethod
    def unpad(data):
        """
        The function removes padding for a given data
        :param data: (bytes) data to be unpad
        :return: (bytes) unpadded data
        """
        assert isinstance(data, bytes)
        return data[:-data[-1]]


if __name__ == '__main__':
    padded = Pad.pad('dawid'.encode())
    print(padded)
    print(Pad.unpad(padded))
