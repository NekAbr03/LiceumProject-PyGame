from pygame.transform import flip
import random
from clases import Collider


class bounceTrait:
    def __init__(self, entity):
        self.vel = 5
        self.jump = False
        self.entity = entity

    def update(self):
        if self.jump:
            self.entity.vel.y = 0
            self.entity.vel.y -= self.vel
            self.jump = False
            self.entity.inAir = True

    def reset(self):
        self.entity.inAir = False


class GoTrait:
    def __init__(self, animation, screen, camera, ent):
        self.animation = animation
        self.direction = 0
        self.heading = 1
        self.accelVel = 0.4
        self.decelVel = 0.25
        self.maxVel = 3.0
        self.screen = screen
        self.boost = False
        self.camera = camera
        self.entity = ent

    def update(self):
        if self.boost:
            self.maxVel = 5.0
            self.animation.deltaTime = 4
        else:
            self.animation.deltaTime = 7
            if abs(self.entity.vel.x) > 3.2:
                self.entity.vel.x = 3.2 * self.heading
            self.maxVel = 3.2

        if self.direction != 0:
            self.heading = self.direction
            if self.heading == 1:
                if self.entity.vel.x < self.maxVel:
                    self.entity.vel.x += self.accelVel * self.heading
            else:
                if self.entity.vel.x > -self.maxVel:
                    self.entity.vel.x += self.accelVel * self.heading

            if not self.entity.inAir:
                self.animation.update()
            else:
                self.animation.inAir()
        else:
            self.animation.update()
            if self.entity.vel.x >= 0:
                self.entity.vel.x -= self.decelVel
            else:
                self.entity.vel.x += self.decelVel
            if int(self.entity.vel.x) == 0:
                self.entity.vel.x = 0
                if self.entity.inAir:
                    self.animation.inAir()
                else:
                    self.animation.idle()
        if (self.entity.invincibilityFrames//2) % 2 == 0:
            self.drawEntity()

    def updateAnimation(self, animation):
        self.animation = animation
        self.update()

    def drawEntity(self):
        if self.heading == 1:
            self.screen.blit(self.animation.image, self.entity.getPos())
        elif self.heading == -1:
            self.screen.blit(
                flip(self.animation.image, True, False), self.entity.getPos()
            )


class JumpTrait:
    def __init__(self, entity):
        self.vertical_speed = -12
        self.jumpHeight = 120
        self.entity = entity
        self.initalHeight = 384
        self.deaccelerationHeight = self.jumpHeight - ((self.vertical_speed*self.vertical_speed)/(2*self.entity.gravity))

    def jump(self, jumping):
        if jumping:
            if not self.entity.inAir and not self.entity.inJump:  # redundant check
                self.entity.sound.play_sfx(self.entity.sound.jump)
                self.entity.vel.y = self.vertical_speed
                self.entity.inAir = True
                self.initalHeight = self.entity.rect.y
                self.entity.inJump = True
                self.entity.obeyGravity = False  # always reach maximum height

        if self.entity.inJump:
            if (self.initalHeight-self.entity.rect.y) >= self.deaccelerationHeight or self.entity.vel.y == 0:
                self.entity.inJump = False
                self.entity.obeyGravity = True

    def reset(self):
        self.entity.inAir = False


class LeftRightWalkTrait:
    def __init__(self, entity, level):
        self.direction = random.choice([-1, 1])
        self.entity = entity
        self.collDetection = Collider(self.entity, level)
        self.speed = 1
        self.entity.vel.x = self.speed * self.direction

    def update(self):
        if self.entity.vel.x == 0:
            self.direction *= -1
        self.entity.vel.x = self.speed * self.direction
        self.moveEntity()

    def moveEntity(self):
        self.entity.rect.y += self.entity.vel.y
        self.collDetection.checkY()
        self.entity.rect.x += self.entity.vel.x
        self.collDetection.checkX()
