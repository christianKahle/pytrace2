from pygame.math import Vector3
import math
class entity():
    def __init__(self,position,direction):
        self.pos = Vector3(position)
        self.rot = Vector3(direction).normalize()
    def rotate(self,degrees,rotation_axis):
        self.rot.rotate_ip(degrees,rotation_axis)
    def move(self,rel):
        self.pos = self.pos + rel
class v_entity(entity):
    def __init__(self,position,direction,color=(0,0,0)):
        super().__init__(position,direction)
        self.color = Vector3(color)
    def raysect(self,ray):
        return False
    def radius(self):
        return 0
    def global_light_color(self,ray,distance,source):
        return [int(i/2+.5) for i in (Vector3(self.color)*max((-self.ray_normal(ray,distance)*source+1),0.25))]
class plane(v_entity):
    def __init__(self,position,direction,color):
        super().__init__(position,direction,color)
        self.radius = 0
    def raysect(self, ray):
        v = self.pos - ray.pos
        try:t = self.rot *v / (self.rot * ray.rot)
        except:return False
        if t > 0:
            return t
        return False
    def ray_normal(self,ray,d):
        d = ray.rot*self.rot > 0
        return self.rot * -(d - int(not d))
class rectangle(plane):
    def __init__(self,position,direction,size,up=(0,0,1),color=(0,0,0)):
        super().__init__(position,direction,color)
        self.size = size
        self.up = Vector3(up).normalize()
        self.xv = self.up.cross(self.rot).normalize()
        self.yv = self.xv.cross(self.rot).normalize()
        self.radius =  (size[0]**2+size[1]**2)**0.5 / 2
    def raysect(self, ray):
        t = super().raysect(ray)
        x = ray.pos + ray.rot * t
        if (abs(x.dot(self.xv)) <= self.size[0]/2 and abs(x.dot(self.yv)) <= self.size[1]/2):
            return t
        return False
class sphere(v_entity):
    def __init__(self,position,direction,radius,color=(0,0,0)):
        super().__init__(position,direction,color)
        self.radius = radius
    def raysect(self, ray):
        v = ray.pos - self.pos
        u = -v.dot(ray.rot)
        for i in [-1,1]:
            t = u+i*(((u**2)+((self.radius**2)-v.length_squared()))**.5)
            if type(t) == float and t > 0:
                return t
        return False
    def ray_normal(self,ray,d):
        y = ray.pos + ray.rot*d
        return (y - self.pos).normalize()
class rectangle_prism(v_entity):
    def __init__(self,position,direction,size,up=(),color=(0,0,0)):
        super().__init__(position,direction,color)
        self.size = Vector3(size)/2
        self.up = Vector3(up)
        self.radius = self.size.length()
        self.m = [self.rot,self.rot.cross(self.up).normalize()]
        self.m.append(self.rot.cross(self.m[1]))
    def raysect(self, ray):
        v = self.pos - ray.pos
        lt = []
        for n in [0,1,2]:
            for i in [-1,1]:
                try:t = (v*self.m[n] + i*self.size[n])/(ray.rot * self.m[n])
                except:t = 0
                x = (t * ray.rot + ray.pos) - self.pos 
                if (abs(x * self.m[(n+1)%3]) <= self.size[(n+1)%3] and abs(x * self.m[(n+2)%3]) <= self.size[(n+2)%3]):lt.append(t)
        small = False
        for t in lt:
            if not small:
                small = t
            elif t < small:
                small = t
        return small
    def ray_normal(self,ray,d):
        n = ray.pos + ray.rot*d - self.pos
        x = n*self.m[0]/self.size[0]
        y = n*self.m[1]/self.size[1]
        z = n*self.m[2]/self.size[2]
        if abs(x) > abs(y) and abs(x) > abs(z):return self.m[0] * math.copysign(1,x)
        if abs(y) > abs(z):return self.m[1] * math.copysign(1,y)
        return self.m[2] * math.copysign(1,z)
