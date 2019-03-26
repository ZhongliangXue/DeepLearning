##定义一个长方形，和它的方法（Test）
class Rectangle(object):
    def __init__(self,width,length,height):
        self.width = width
        self.length = length
        self.height = height

    def getWidth(self):
        return self.width

    def setWidth(self,width):
        self.width = width

    def getLength(self):
        return self.length

    def setLength(self,length):
        self.length = length

    def area(self):
        return self.length * self.width

    def volume(self):
        return self.length * self.width * self.height

if __name__ == '__main__':
    ractA = Rectangle(20,10,30)
    print('长方体的体积是：',ractA.volume())