from pygame.math import Vector3
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
        try:
            t = self.rot.dot(v) / self.rot.dot(ray.rot)
        except:
            return False
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
        t = False
        for i in range(-1,2,2):
            t_temp = u+i*(((u**2)+((self.radius**2)-v.length_squared()))**.5)
            if type(t_temp) == float and t_temp > 0:
                t = t_temp
                break
        return t
    def ray_normal(self,ray,d):
        y = ray.pos + ray.rot*d
        return (y - self.pos).normalize()
class rectangle_prism(v_entity):
    def __init__(self,position,direction,size,up=(),color=(0,0,0)):
        super().__init__(position,direction,color)
        self.size = Vector3(size)/2
        self.up = Vector3(up)
        self.radius = self.size.length()
        self.r2 = self.radius**2
        xd = self.rot * self.size.x
        yd = self.rot.cross(self.up).normalize() * self.size.y
        zd = xd.cross(yd).normalize() * self.size.z
        self.m = xd + yd + zd
    def raysect(self, ray):
        v = self.pos - ray.pos
        t = False
        try:t = (self.r2-self.m * v) / (self.m * self.d)
        except:pass
        return t
    def ray_normal(self,ray,d):
        y = ray.pos + ray.rot*d
        return (y - self.pos).normalize()