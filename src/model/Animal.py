import pygame
import random
import math

# Initialize Pygame
pygame.init()


# Configuration variables
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
ANIMAL_WIGHT = 50
ANIMAL_HEIGHT = 20
MAX_SPEED = 10
THETA = math.pi/2

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)


# Class of Animals
class Animal:
    def __init__(self):
        self.pos = [SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2]
        self.image = pygame.Surface((ANIMAL_WIGHT, ANIMAL_HEIGHT), pygame.SRCALPHA)
        self.velocity = self.create_random_vector()

        self.update_beard()

    def create_random_vector(self):
        """
        This function will create a vector with random magnitude and direction.
        :return
            - A vector with random magnitude and direction, tuple
            - angle: direction of velocity in degree
        """
        angle = random.uniform(0, 2 * math.pi)
        magnitude = random.uniform(0, MAX_SPEED)
        return magnitude * math.cos(angle), magnitude * math.sin(angle)
    
    def create_right_vector(self):
        """
        This function will create a velocity in the right of the current velocity
        """
        angle = find_angle(self.velocity) + math.pi/2
        magnitude = random.uniform(0, MAX_SPEED)
        return magnitude * math.cos(angle), magnitude * math.sin(angle)
    
    def create_left_vector(self):
        """
        This function will create a velocity in the left of the current velocity
        """
        angle = find_angle(self.velocity) - math.pi/2
        magnitude = random.uniform(0, MAX_SPEED)
        return magnitude * math.cos(angle), magnitude * math.sin(angle)
    
    def create_opposite_vector(self):
        """
        This function will create a velocity opposite of the current velocity
        """
        angle = find_angle(self.velocity) - math.pi
        magnitude = random.uniform(0, MAX_SPEED)
        return magnitude * math.cos(angle), magnitude * math.sin(angle)
    
    def calcul_velocity_length(self) -> float:
        """
        This funciton calcul the length of the current velocity
        """
        return math.sqrt(self.velocity[0] ** 2 + self.velocity[1] ** 2)

    def limit_speed(self):
        """
        This function will make sure the speed is less than maximum speed
        """
        velocity_length = self.calcul_velocity_length()
        if velocity_length > MAX_SPEED:
            self.velocity = (self.velocity[0] / velocity_length * MAX_SPEED, self.velocity[1] / velocity_length * MAX_SPEED)

    def update_position(self):
        """
        This function will update the position of the animal based on the current speed
        """
        self.pos[0] += self.velocity[0]
        self.pos[1] += self.velocity[1]
    
    def update_beard(self):
        """
        This function will update the position of the all beards
        """
        self.beard_right = self.beard_right_update()
        self.beard_left = self.beard_left_update()
        self.beard_middle = self.beard_middle_update()

    def update_velocity(self):
        """
        This function will add the random velocity vector to the animal's current velocity vector
        """
        self.update_beard()
        
        # Detect collide :
        if self.beard_middle_in_collide() == False:
            if self.beard_right_in_collide():
                self.velocity = self.create_left_vector()
            elif self.beard_left_in_collide():
                self.velocity = self.create_right_vector()
        
        elif self.beard_right_in_collide() and self.beard_left_in_collide(): # When the animal in the corner
            self.velocity = self.create_opposite_vector()

        elif self.beard_middle_in_collide():
            if self.beard_right_in_collide():
                self.velocity = self.create_left_vector()
            elif self.beard_left_in_collide():
                self.velocity = self.create_right_vector()
            else:
                self.velocity = self.create_left_vector()
                self.update_beard()
                if self.beard_middle_in_collide():
                    self.velocity = self.create_opposite_vector()
        
        else:
            new_vector = self.create_random_vector()
            # Add the random velocity vector to the antimal's current velocity vector
            self.velocity = (self.velocity[0] + new_vector[0], self.velocity[1] + new_vector[1])

        # Limit the animal's speed
        self.limit_speed()

    def beard_right_update(self) -> list:
        """
        Update the position of the beard middle
        """
        velocity_length = self.calcul_velocity_length()
        angle = find_angle(self.velocity)
        beard_direction = MAX_SPEED * math.cos(angle + THETA), \
                        MAX_SPEED * math.sin(angle + THETA)
    
        return [self.pos[0] + self.velocity[0]/velocity_length * ANIMAL_WIGHT + beard_direction[0], \
            self.pos[1] + self.velocity[1]/velocity_length * ANIMAL_WIGHT + beard_direction[1]]
    
    def beard_left_update(self) -> list:
        """
        Update the position of the beard middle
        """
        velocity_length = self.calcul_velocity_length()
        angle = find_angle(self.velocity)
        beard_direction = MAX_SPEED * math.cos(angle - THETA), \
                        MAX_SPEED * math.sin(angle - THETA)
    
        return [self.pos[0] + self.velocity[0]/velocity_length * ANIMAL_WIGHT + beard_direction[0], \
            self.pos[1] + self.velocity[1]/velocity_length * ANIMAL_WIGHT + beard_direction[1]]
    
    def beard_middle_update(self) -> list:
        """
        Update the position of the beard middle
        """
        velocity_length = self.calcul_velocity_length()
    
        return [self.pos[0] + self.velocity[0]/velocity_length * (ANIMAL_WIGHT + MAX_SPEED), \
            self.pos[1] + self.velocity[1]/velocity_length * (ANIMAL_WIGHT + MAX_SPEED)]

    def beard_right_in_obstacle(self) -> bool:
        """
        Verify if the beard right in obstacle
        """
        pass

    def beard_left_in_obstacle(self) -> bool:
        """
        Verify if the beard left in obstacle
        """
        pass

    def beard_middle_in_obstacle(self) -> bool:
        """
        Verify if the beard middle in obstacle
        """
        pass

    def beard_right_out_screen(self) -> bool:
        """
        Verify if the beard right is out of the screen
        """
        return self.beard_right[0] > SCREEN_WIDTH or self.beard_right[0] < 0 or \
                self.beard_right[1] > SCREEN_HEIGHT or self.beard_right[1] < 0

    def beard_left_out_screen(self):
        """
        Verify if the beard left is out of the screen
        """
        return self.beard_left[0] > SCREEN_WIDTH or self.beard_left[0] < 0 or \
                self.beard_left[1] > SCREEN_HEIGHT or self.beard_left[1] < 0
    
    def beard_middle_out_screen(self) -> bool:
        """
        Verify if the beard middle is out of the screen
        """
        return self.beard_middle[0] > SCREEN_WIDTH or self.beard_middle[0] < 0 or \
                self.beard_middle[1] > SCREEN_HEIGHT or self.beard_middle[1] < 0

    def beard_right_in_collide(self) -> bool:
        """
        Verify if the beard right is in collide
        """
        return self.beard_right_out_screen() or self.beard_right_in_obstacle()
    
    def beard_left_in_collide(self) -> bool:
        """
        Verify if the beard left is in collide
        """
        return self.beard_left_out_screen() or self.beard_middle_in_obstacle()
    
    def beard_middle_in_collide(self) -> bool:
        """
        Verify if the beard middle is in collide
        """
        return self.beard_middle_out_screen() or self.beard_middle_in_obstacle()


# Fonctions
def find_angle(velocity):
    """
    This function will find the direction of a velocity
    :return
        - angle: float (in radians)
    """
    angle = math.atan2(velocity[1], velocity[0])
    if angle < 0:
        angle += 2 * math.pi
    return angle

def new_direction_image(image, angle, position):
    """
    This function will rotate the rectangle in the direction of the velocity vector and draw it on the screen
    :param
        - image: image of animal
        - angle: angle in radians corresponds to the velocity at the next moment, float
        - position: position of animal, tuple
    """
    rotated_image = pygame.transform.rotate(image, -math.degrees(angle)) # Negative angle amounts will rotate clockwise.
    animal_rect = rotated_image.get_rect(center=position)
    screen.fill(BLACK)
    screen.blit(rotated_image, animal_rect)
    return rotated_image

def new_position_image(screen, new_position, rotated_image) -> None:
    """
    This function will draw on the screen the animal with it's new position without change of direction
    :param
        - screen: the window of pygame
        - new_position: the new position of animal, tuple
        - rotated_image: the image of animal with it's direction
    """
    animal_rect = rotated_image.get_rect(center=new_position)
    screen.fill(BLACK)
    screen.blit(rotated_image, animal_rect)



# Initialize the Pygame screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Load image
animal = Animal()
pygame.draw.rect(animal.image, WHITE, (0, 0, ANIMAL_WIGHT, ANIMAL_HEIGHT))

# Angle calculation
angle = find_angle(animal.velocity)

# Main loop
running = True
i = 0
while running:
    # Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if i%2 == 0:
        # New direction
        rotated_image = new_direction_image(animal.image, angle, animal.pos)
    else:
        # New position
        animal.update_position()
        new_position_image(screen, animal.pos, rotated_image)
        # New velocity
        animal.update_velocity()
        # New angle
        angle = find_angle(animal.velocity)

    # Draw on the screen
    pygame.display.flip()
    pygame.time.delay(50)

    i+=1

# End
pygame.quit()