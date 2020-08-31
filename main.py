import pygame, math, time
from entities import *
size = (240,135)
screen = pygame.display.set_mode(size,pygame.SCALED)
pygame.mouse.set_visible(False)
playerSettings = {
"up"          : pygame.math.Vector3(0,0,1),
"fwd"         : pygame.math.Vector3(1,0,0),
"look_angles" : (0,0),
"looking"     : pygame.math.Vector3(1,0,0),
"fov"         : math.radians(90),
"sensitivity" : 0.75,
"scroll_sense": math.radians(10),
"position"    : pygame.math.Vector3(0,0,0),
"speed"       : .2,
"render_dist" : 35,
"frustum_calc": (16,9)
}

pygame.font.init()
global_light_dir = -pygame.Vector3(1,1,1).normalize()
font = pygame.font.SysFont("couriernew", 14)
pygame.mouse.set_pos(size[0]//2,size[1]//2)
pygame.event.get()

#MAKE SURE TO UNCOMMENT THESE ENTITIES FOR THEM TO SHOW UP
#inf_plane IS A PLANE WITHOUT LIMITS, IN THIS CASE, THE GROUND

ents = [ 
#plane((0,0,-1),(0,0,1),color=(0,0,0)),
#plane((0,-1,0),(0,1,0),color=(200,0,0)),
#rectangle((1,0,0),(1,0,0),(3,1),color=(200,20,20)),
#rectangle((0.85,-0.15,0.1),(1,1,1),(1,0.5),up=(1,0,1),color=(20,20,200)),
#sphere((1.15,0,0),(1,0,0),0.35,color=(255,255,55))
rectangle_prism((3,0,0),(1,1,1.3),(1,2,1.5),(0,0,1),(30,230,130))
]

def rotation(playerInfo,event):
    look_angles = playerInfo["look_angles"]
    up = playerInfo["up"]
    sensitivity = playerInfo["sensitivity"]
    xd = (event.pos[0]-size[0]//2)*sensitivity
    yd = (event.pos[1]-size[1]//2)*sensitivity
    x = (xd + look_angles[0] + 180) % 360 - 180
    y = max(min(-yd + look_angles[1],89.99),-89.99)
    playerInfo["look_angles"] = (x,y)
    if abs(x)+abs(y) > 0:
        fwd = playerInfo["fwd"].rotate(x,up)
        orth = fwd.cross(up).normalize()
        looking = fwd.rotate(y,orth)
        playerInfo["looking"] = looking
    if pygame.display.get_active():
        pygame.mouse.set_pos(size[0]//2,size[1]//2)
    

def zoom(playerInfo,event):
    b = event.button == 5
    fov = playerInfo["fov"]
    zoom = playerInfo["scroll_sense"]*(b - int(not b))+fov
    if math.radians(30) < zoom <= math.radians(150):
        playerInfo["fov"] = zoom

movement = {
    pygame.K_w:lambda pos,fwd,up,speed: pos + fwd * speed,
    pygame.K_s:lambda pos,fwd,up,speed: pos - fwd * speed,
    pygame.K_d:lambda pos,fwd,up,speed: pos - fwd.cross(up) * speed,
    pygame.K_a:lambda pos,fwd,up,speed: pos + fwd.cross(up) * speed,
    pygame.K_SPACE:lambda pos,fwd,up,speed: pos + up * speed,
    pygame.K_LSHIFT:lambda pos,fwd,up,speed: pos - up * speed,
}
def move(playerInfo):
    pos, fwd, up, speed = playerInfo["position"], playerInfo["looking"], playerInfo["up"], playerInfo["speed"]
    pressed = pygame.key.get_pressed()
    for i in movement:
        if pressed[i]:
            pos = movement.get(i,lambda pos,fwd,up,speed: pos)(pos,fwd,up,speed)
    playerInfo["position"] = pos

def processEvents(events,playerInfo):
    close_action = False
    for event in events:
        if event.type == pygame.QUIT:
            close_action = True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DELETE or event.key == pygame.K_BACKSPACE:
                close_action = True
        if event.type == pygame.MOUSEMOTION:
            rotation(playerInfo,event)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button in [4,5]:
                zoom(playerInfo,event)
    return not close_action

def ray(entities,direction,playerInfo,x,y):
    r = entity(playerInfo["position"],direction)
    short_len = False
    shortest = False
    for e in entities:
        p = e.raysect(r)
        if p:
            if not short_len or p < short_len:
                short_len = p
                shortest = e
    if shortest:
        #if x == size[0]//2 and y == size[1]//2:text = font.render(str([round(i,2) for i in (r.pos + r.rot * short_len)]),False,(255,255,255),(0,0,0,100));screen.blit(text,text.get_rect())
        pygame.draw.rect(screen,shortest.global_light_color(r,short_len,global_light_dir),(x,y,1,1))
    return short_len

def max_distance(entities,playerInfo):
    return [entity for entity in entities if (entity.pos-playerInfo["position"]).length()-entity.radius < playerInfo["render_dist"]]

def frustum(entities,topleft,botright,up,pos):
    left = -topleft.cross(up).normalize()
    right = botright.cross(up).normalize()
    for n in left,right:
        entities = [e for e in entities if (e.pos - pos) * n + e.radius > 0]
    return entities
    


def update(playerInfo,entity_list):
    screen.fill((0,0,0))
    entity_list = max_distance(entity_list,playerInfo)
    looking = playerInfo["looking"]
    up = playerInfo["up"]
    fov = playerInfo["fov"]
    refrustum = playerInfo["frustum_calc"]
    x_delta = up.cross(looking).normalize()/size[0]*math.tan(fov/2)
    y_delta = x_delta.cross(looking)
    ents = []
    for y_mul in range(size[1]//refrustum[1]):
        y2 = y_mul*refrustum[1]
        for x_mul in range(size[0]//refrustum[0]):
            x2 = x_mul*refrustum[0]
            ents = frustum(entity_list,(looking + x_delta*(2*x2-size[0]) + y_delta*(2*y2-size[1])).normalize(),(looking + x_delta*(2*(x2+refrustum[0]-1)-size[0]) + y_delta*(2*(y2+refrustum[1]-1)-size[1])).normalize(),up,playerInfo["position"])
            for y in range(refrustum[1]):
                y_n = y_delta*(2*(y+y2)-size[1])
                for x in range(refrustum[0]):
                    x_n = x_delta*(2*(x+x2)-size[0])
                    look = (looking + x_n + y_n).normalize()
                    ray(ents,look,playerInfo,x+x2,y+y2)

    pygame.draw.rect(screen,(120,120,120),(size[0]//2,size[1]//2,1,1))
        
    

current_info = None
while(processEvents(pygame.event.get(),playerSettings)):
    move(playerSettings)
    if current_info != playerSettings:
        update(playerSettings,ents)
    pygame.display.flip()
    current_info = playerSettings.copy()
pygame.quit()