import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np

# --- Variáveis de Estado da Câmera ---
cam_rot_x = 30.0   
cam_rot_y = -45.0  
cam_zoom  = -30.0  
mouse_down = False
last_mouse_pos = (0, 0)

font = None

# P1 = np.array([-2.0, 0.0, 2.0])
# P2 = np.array([ 2.0, 0.0, 2.0])
# P3 = np.array([0.0, -2.0, 2.0])
# P4 = np.array([0.0,  2.0, 2.0])

P1 = np.array([0.0, 0.0, 0.0])
P2 = np.array([4.0, 4.0, 4.0])
P3 = np.array([2.0, 0.0, 4.0])
P4 = np.array([2.0, 4.0, 0.0])

# P1 = np.array([-2.0, 0.0, -2.0])
# P2 = np.array([ 4.0, 0.0, -2.0])

# P3 = np.array([1.0,  3.0, 1.0])
# P4 = np.array([1.0, -3.0, -5.0])

def init_gl(width, height):
    glClearColor(0.1, 0.1, 0.1, 1.0)
    glEnable(GL_DEPTH_TEST)
    
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, (width / height), 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)

def draw_text(x, y, text, color=(255, 255, 255)):
    global font
    textSurface = font.render(text, True, color, (0,0,0,0)) 
    textData = pygame.image.tostring(textSurface, "RGBA", True)
    w, h = textSurface.get_width(), textSurface.get_height()
    
    glRasterPos2i(x, y)
    glDrawPixels(w, h, GL_RGBA, GL_UNSIGNED_BYTE, textData)

def draw_hud(width, height):    
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    
    gluOrtho2D(0, width, height, 0)
    
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    glDisable(GL_DEPTH_TEST)
        
    margin = 20
    line_height = 25
    
    # Legenda Eixo X (Vermelho)
    draw_text(margin, height - margin, "Eixo X", (255, 100, 100))
    
    # Legenda Eixo Y (Verde)
    draw_text(margin, height - margin - line_height, "Eixo Y", (100, 255, 100))
    
    # Legenda Eixo Z (Azul)
    draw_text(margin, height - margin - (line_height*2), "Eixo Z", (100, 100, 255))

    # Volta pro 3D
    glEnable(GL_DEPTH_TEST)
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_axes_and_grid():
    glLineWidth(1)
    glColor3f(0.3, 0.3, 0.3)
    glBegin(GL_LINES)
    grid_size = 10
    for i in range(-grid_size, grid_size + 1):
        glVertex3f(-grid_size, 0, i)
        glVertex3f(grid_size, 0, i)
        glVertex3f(i, 0, -grid_size)
        glVertex3f(i, 0, grid_size)
    glEnd()

    glLineWidth(3)
    glBegin(GL_LINES)

    # Eixo X (Vermelho)
    glColor3f(1.0, 0.0, 0.0)
    glVertex3f(0, 0, 0); glVertex3f(20, 0, 0)

    # Eixo Y (Verde)
    glColor3f(0.0, 1.0, 0.0)
    glVertex3f(0, 0, 0); glVertex3f(0, 20, 0)

    # Eixo Z (Azul)
    glColor3f(0.0, 0.0, 1.0)
    glVertex3f(0, 0, 0); glVertex3f(0, 0, 20)
    glEnd()

    glLineWidth(1)
    glColor3f(0.5, 0.0, 0.0); glBegin(GL_LINES); glVertex3f(0,0,0); glVertex3f(-20,0,0); glEnd() # -X
    glColor3f(0.0, 0.5, 0.0); glBegin(GL_LINES); glVertex3f(0,0,0); glVertex3f(0,-20,0); glEnd() # -Y
    glColor3f(0.0, 0.0, 0.5); glBegin(GL_LINES); glVertex3f(0,0,0); glVertex3f(0,0,-20); glEnd() # -Z

def draw_points_and_line(p1, p2, pointsColor, lineColor):
    glColor3fv(pointsColor)
    glPointSize(8)
    glBegin(GL_POINTS)
    glVertex3fv(p1)
    glVertex3fv(p2)
    glEnd()

    # Cálculo Paramétrico (Equação Vetorial)
    # R(t) = origin + t * direction
    direction = p2 - p1 
    origin = p1

    scale = 100.0 
    p_start = origin - (direction * scale)
    p_end   = origin + (direction * scale)

    glColor3fv(lineColor)
    glLineWidth(2)
    glBegin(GL_LINES)
    glVertex3fv(p_start)
    glVertex3fv(p_end)
    glEnd()
    
    return (origin, direction)

def calculate_parametric_intersection(line1_data, line2_data):
    #Calcula a intersecção entre duas retas.
    p1, d1 = line1_data
    p2, d2 = line2_data
    
    w0 = p1 - p2

    # Produtos escalares para o sistema linear (Mínimos Quadrados)
    a = np.dot(d1, d1)
    b = np.dot(d1, d2)
    c = np.dot(d2, d2)
    d = np.dot(w0, d1)
    e = np.dot(w0, d2)

    denom = a * c - b * b
    if denom < 1e-6:
        return None 

    # Calcula os parâmetros escalares t e u
    t = (b * e - c * d) / denom
    u = (a * e - b * d) / denom

    # Encontra os pontos geométricos
    point_on_r1 = p1 + (t * d1)
    point_on_r2 = p2 + (u * d2)
    
    # Se os pontos são os mesmos, há interseção
    if (point_on_r1 == point_on_r2).all():
        return point_on_r1
    
    return None

def draw_perpendicular_vector(intersection_point, line1_data, line2_data):
    _, d1 = line1_data
    _, d2 = line2_data

    # Calcula o Produto Vetorial
    normal_vector = np.cross(d1, d2)

    length = np.linalg.norm(normal_vector)
    if length < 1e-6:
        return

    visual_vector = (normal_vector / length) * 20.0
    
    glColor3f(1.0, 1.0, 1.0)
    glLineWidth(4)
    
    glBegin(GL_LINES)
    glVertex3fv(intersection_point - visual_vector)
    glVertex3fv(intersection_point + visual_vector)
    glEnd()

def main():
    global cam_rot_x, cam_rot_y, cam_zoom, mouse_down, last_mouse_pos, font
    
    pygame.init()
    display = (800, 600)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    pygame.display.set_caption("Visualizador Geométrico - Plano Cartesiano 3D")
    
    pygame.font.init()
    font = pygame.font.SysFont('Arial', 24, bold=True)
    
    init_gl(display[0], display[1])

    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); quit()
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_down = True
                    last_mouse_pos = pygame.mouse.get_pos()
                elif event.button == 4: cam_zoom += 0.5
                elif event.button == 5: cam_zoom -= 0.5
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1: mouse_down = False
            
            elif event.type == pygame.MOUSEMOTION and mouse_down:
                x, y = pygame.mouse.get_pos()
                dx, dy = x - last_mouse_pos[0], y - last_mouse_pos[1]
                cam_rot_y += dx * 0.5
                cam_rot_x += dy * 0.5
                last_mouse_pos = (x, y)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        # Desenha Cena 3D
        glTranslatef(0.0, 0.0, cam_zoom)
        glRotatef(cam_rot_x, 1, 0, 0)
        glRotatef(cam_rot_y, 0, 1, 0)

        draw_axes_and_grid()

        line1_param = draw_points_and_line(P1, P2, [1.0, 1.0, 0.0], [1.0, 1.0, 0.0])
        line2_param = draw_points_and_line(P3, P4, [1.0, 0.0, 1.0], [1.0, 0.0, 1.0])

        intersection = calculate_parametric_intersection(line1_param, line2_param)
        if intersection is not None:
            glColor3f(0.0, 1.0, 0.0)
            glPointSize(12)
            glBegin(GL_POINTS)
            glVertex3fv(intersection)
            glEnd()

            draw_perpendicular_vector(intersection, line1_param, line2_param)

        # Desenha Hud 2D
        draw_hud(display[0], display[1])

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()