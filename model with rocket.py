import sys
import pygame
import numpy as np

from pygame.locals import *  # for K_RIGHT. K_c etc...

SCREEN_WIDTH = 900
SCREEN_HEIGHT = 650

GRIS = (200, 200, 200)
ROUGE = (255, 77, 0)
BLEU = (14, 236, 252)
JAUNE = (255, 230, 0)
ORANGE = (255, 179, 0)
BLANC = (255, 255, 255)
NOIR = (0, 0, 0)
BLEUFONCE = (0, 60, 181)

# TERRESTRIAL
VERT_BLANC = (176, 249, 185)
# SUPER EARTH
VERT = (40, 220, 85)
# GAS GIANT
MAUVE = (255, 37, 212)
# NEPTUNE-LIKE
BLEUMAT = (160, 158, 235)

types_stars = ["O", "B", "A", "F", "G", "K", "M"]
types_planets = ["Terrestrial", "Super Earth", "Neptune-Like", "Gas Giant"]
planets = []


class Rocket:

    def __init__(self, nom_fichier):
        self.iGauche, self.iDroite = self.load_images(nom_fichier)
        self.surface = pygame.image.load(nom_fichier).convert()
        self.rect = self.surface.get_rect()
        self.current_image = self.iDroite
        self.vitesse = 2  # random.choice([-2, 2])

    def load_images(self, nom_fichier):

        image_g = pygame.image.load(nom_fichier).convert()
        image_g.set_colorkey(image_g.get_at((0, 0)), pygame.RLEACCEL)
        image_d = pygame.transform.flip(image_g, True, False)

        return image_g, image_d

    def update(self, keys):
        """
        Update du rectangle pour chaque changement de frame
        """

        if keys[K_LEFT]:
            self.current_image = self.iGauche
            if self.rect.x <= 0:
                self.rect.x = self.rect.x
            else:
                self.rect.x -= self.vitesse

        if keys[K_RIGHT]:
            self.current_image = self.iDroite
            if self.rect.x >= SCREEN_WIDTH - 260:
                self.rect.x = self.rect.x
            else:
                self.rect.x += self.vitesse

        if keys[K_UP]:
            if self.rect.y <= 0:
                self.rect.y = self.rect.y
            else:
                self.rect.y -= self.vitesse

        if keys[K_DOWN]:
            if self.rect.y >= SCREEN_HEIGHT - 260:
                self.rect.y = self.rect.y
            else:
                self.rect.y += self.vitesse

    def draw(self, surface):
        """
        Dessine l'objet sur la surface passee en paramètre
        """
        surface.blit(self.current_image, self.rect)


class Star:
    def __init__(self, diameter, visualdiameter, mass, type):
        self.diameter = diameter * 55
        self.visualdiameter = visualdiameter * 45
        self.actualdiameter = diameter
        self.mass = mass
        self.type = type
        self.surface = pygame.Surface((self.diameter, self.diameter), pygame.SRCALPHA)
        self.rect = self.surface.get_rect()
        self.rect.x, self.rect.y = (453-self.visualdiameter/2), (329-self.visualdiameter/2)
        self.colour = self.choose_colour()

        pygame.draw.circle(self.surface, self.colour, (self.visualdiameter/2, self.visualdiameter/2), self.visualdiameter/2)
        # pygame.draw.circle(self.surface, NOIR, (10, 10), 10)

    def draw(self, surface):
        """
        Dessine l'objet sur la surface passee en paramètre
        """
        surface.blit(self.surface, self.rect)

    def choose_colour(self):
        colour = (0, 0, 0)
        if self.type == "O" or "B" or "A" or "F":
            colour = BLEU
        if self.type == "G":
            colour = JAUNE
        if self.type == "K":
            colour = ORANGE
        if self.type == "M":
            colour = ROUGE
        return colour


class Planet:
    def __init__(self, distance, diameter, visualdistance, visualdiameter, mass, orbittime, nbmoons, type):
        # for visual
        self.distance = visualdistance * 280
        # actually good
        self.actualdistance = distance

        # actually good
        self.diameter = diameter
        # for visual
        self.visualdiameter = visualdiameter * 15

        self.nbmoons = nbmoons
        self.orbittime = orbittime
        self.mass = mass
        self.type = type

        self.colour = self.find_colour()

        self.speed = 2*float(self.distance)*3.1415927/self.orbittime

        self.surface = pygame.Surface((self.visualdiameter, self.visualdiameter), pygame.SRCALPHA)
        self.rect = self.surface.get_rect()
        self.rect.x, self.rect.y = SCREEN_WIDTH/2-self.distance, SCREEN_HEIGHT/2+self.visualdiameter/2

        pygame.draw.circle(self.surface, self.colour, (self.visualdiameter/2, self.visualdiameter/2), self.visualdiameter/2)

        # for update
        self.sunPosition = (SCREEN_WIDTH/2, SCREEN_HEIGHT/2)
        self.radTravelled = 0
        # totalDistance = distance
        self.rad = 0.02 * 2 * 3.14/(orbittime/25)

    def find_colour(self):
        colour1 = (0, 0, 0)
        index = types_planets.index(self.type)
        if index == 0:
            colour1 = VERT_BLANC
        elif index == 1:
            colour1 = VERT
        elif index == 2:
            colour1 = BLEUMAT
        elif index == 3:
            colour1 = MAUVE
        return colour1

    def draw(self, surface):
        """
        Dessine l'objet sur la surface passee en paramètre
        """
        surface.blit(self.surface, self.rect)

    def update(self):

        self.rect.x = self.distance * np.cos(self.radTravelled) + self.sunPosition[0]
        self.rect.y = self.distance * np.sin(self.radTravelled) + self.sunPosition[1]

        self.radTravelled += self.rad


class Background:

    def __init__(self):

        # création de la surface et récupération du Rect() associé
        self.image = self.set_image()
        self.rect = self.image.get_rect()

    def set_image(self):
        """
        Attribution du .png
        """
        image = pygame.image.load("other space background cropped.jpg").convert()
        return image

    def draw(self, surface):
        """
        Blit l'image sur la surface passée en parametre
        """
        surface.blit(self.image, self.rect)


class App:
    def __init__(self):
        """
        Creation de l'objet rectangle apres avoir initialisé et recuperer
        la surface de la fenêtre
        """

        self.filename = self.choose()
        file = open(self.filename, "r")
        lines = file.readlines()
        nb_planets = int(lines[0])

        star_diameter, star_visualdiameter, star_mass, star_type = float(lines[1]), float(lines[2]), float(lines[3]), types_stars[int(lines[4])],
        self.star = Star(star_diameter, star_visualdiameter, star_mass, star_type)

        for i in range(nb_planets):
            index = int(5+(i*8))
            planet_distance = float(lines[index])
            planet_diameter = float(lines[index+1])
            planet_visualdistance = float(lines[index+2])
            planet_visualdiameter = float(lines[index+3])
            planet_mass = float(lines[index+4])
            orbittime = float(lines[index+5])
            nbmoons = int(lines[index+6])
            planet_type = types_planets[int(lines[index+7])]

            planet = Planet(planet_distance, planet_diameter, planet_visualdistance, planet_visualdiameter, planet_mass, orbittime, nbmoons, planet_type)
            planets.append(planet)

        file.close()

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Exoplanetary System Observer")
        self.quit = False
        self.keys = pygame.key.get_pressed()

        # creation du rectangle
        self.rectangle = Rocket("rocket_small.png")

        # creation du background ( ou load image)
        self.background = Background()

        self.clock = pygame.time.Clock()
        self.clock.tick(60)
        self.tick_progress = 0

        self.days = 0

        self.start_ticks = pygame.time.get_ticks()  # starter tick

    def choose(self):
        print("\nThis is a simulation of our solar system and all neighboring stars with orbiting planets discovered within 16.08 light years from us.\n" +
              "The youngest stars are in blue, and are either O, B, A or F type. Yellow stars are smaller, and are G type. K stars are coloured in orange\n" +
              "and are 50 000 years old. The red stars are the oldest; M type and over 200 000 years old.\n\n" +
              "Orbiting these stars exist 4 types of planets or exoplanets. Light-green planets are terrestrial planets, such as Earth." +
              "They are found in the \nhabitable zone and are most likely to harbour life. The dark green planets are super earths; "+
              "planets larger than earth but substantially smaller \nthan the other gas and ice planets found in our Universe." +
              "In blue are the gas giants; such as Jupiter. Lastly, dark blue corresponds to planets \nthat are Neptune-like. These " +
              "are smaller than gas giants and found far from their star, giving them a very chilly atmospheric temperature.\n\n")
        print("Observe the planetary systems of exoplanets! Pick a star, and the model will appear in another window.")

        question = str(input("What system would you like to observe?\n\n1. Our Solar System\n2. The Earth by itself (for comparison)\n3. Proxima Centauri\n4. Epsilon Eridani\n5. Tau Ceti\n6. Gliese 876\n\n"))
        filename = question + ".txt"

        return filename

    def event_handler(self):
        """
        capture des évenements clavier
        """

        for event in pygame.event.get():

            if event.type == pygame.QUIT or self.keys[pygame.K_ESCAPE]:
                self.quit = True

            elif event.type in (pygame.KEYUP, pygame.KEYDOWN):
                self.keys = pygame.key.get_pressed()

    def show_info(self):
        font = pygame.font.SysFont("Times New Roman", 15)
        self.screen.blit(font.render("t = " + str(self.days) + " Earth days", True, BLANC), (SCREEN_WIDTH/2 - 40, 5))

        star_type = "Star Type: " + self.star.type
        star_mass = "Star Mass:" + str(self.star.mass) + " solar masses"
        star_diameter = "Star Diameter: " + str(self.star.actualdiameter*1392000) + " km"
        self.screen.blit(font.render(star_type, True, BLANC), (0, 580))
        self.screen.blit(font.render(star_mass, True, BLANC), (0, 600))
        self.screen.blit(font.render(star_diameter, True, BLANC), (0, 620))

        self.planet = planets[0]
        planet_type = "Planet Type: " + self.planet.type
        planet_mass = "Planet Mass:" + str(self.planet.mass) + " times Earth's mass"
        planet_diameter = "Planet Diameter: " + str(self.planet.diameter*12726) + " km"
        planet_distance = "Distance from Star: " + str(self.planet.actualdistance) + " au"
        planet_moons = "Number of Moons: " + str(self.planet.nbmoons)
        planet_orbit = "Orbit time: " + str(self.planet.orbittime) + " Earth days"
        self.screen.blit(font.render(planet_type, True, BLANC), (440, 580))
        self.screen.blit(font.render(planet_mass, True, BLANC), (440, 600))
        self.screen.blit(font.render(planet_diameter, True, BLANC), (440, 620))
        self.screen.blit(font.render(planet_distance, True, BLANC), (720, 580))
        self.screen.blit(font.render(planet_moons, True, BLANC), (720, 600))
        self.screen.blit(font.render(planet_orbit, True, BLANC), (720, 620))

    def update(self):
        """
        Mise à jour des attributs de chaque rectangle en fonction des
        évènements capturés
        """
        self.rectangle.update(self.keys)

        for planet in planets:
            planet.update()

        if self.tick_progress % 2 == 0:
            self.days += 1

    def draw(self):
        """
        Dessine tout ce qu'il y a a dessiner sur la surface
        """
        # REF : blit(source, dest, area=None, special_flags = 0) -> Rect
        # on efface tout.

        self.background.draw(self.screen)

        # puis on dessine tout ce qu’il y a à dessiner.
        # Dans ce cas-ci :juste un rectangle

        self.rectangle.draw(self.screen)

        self.star.draw(self.screen)

        for planet in planets:
            planet.draw(self.screen)

        self.show_info()

    def render(self):
        """
        Appelée apres les update().
        pousse la surface temporaire sur l'écran visible
        """
        pygame.display.flip()

    def boucle_principale(self):
        while not self.quit:
            pygame.time.delay(10)
            self.event_handler()
            self.update()
            self.draw()
            self.render()
            self.tick_progress += 1


def main():
    """
    Initialise la fenêtre, prépare la surface et initialise le programme
    """
    pygame.init()
    app = App()
    app.boucle_principale()
    on_quit()


def on_quit():
    print("Merci et au revoir...")
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
