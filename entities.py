from copy import copy
import pygame
import clases
import traits


class EntityBase(object):
    def __init__(self, x, y, gravity):
        self.vel = clases.Vec2D()
        self.rect = pygame.Rect(x * 32, y * 32, 32, 32)
        self.gravity = gravity
        self.traits = None
        self.alive = True
        self.timeAfterDeath = 5
        self.timer = 0
        self.type = ""
        self.onGround = False
        self.obeyGravity = True

    def applyGravity(self):
        if self.obeyGravity:
            self.vel.y += self.gravity

    def updateTraits(self):
        for trait in self.traits.values():
            try:
                trait.update()
            except AttributeError:
                pass

    def getPosIndex(self):
        return clases.Vec2D(self.rect.x // 32, self.rect.y // 32)

    def getPosIndexAsFloat(self):
        return clases.Vec2D(self.rect.x / 32.0, self.rect.y / 32.0)


class Item(clases.Dashboard):
    def __init__(self, collection, screen, x, y):
        super(Item, self).__init__("./data/font.png", 8, screen)
        self.ItemPos = clases.Vec2D(x, y)
        self.itemVel = clases.Vec2D(0, 0)
        self.screen = screen
        self.coin_animation = copy(collection.get("coin-item").animation)
        self.sound_played = False

    def spawnCoin(self, cam, sound, dashboard):
        if not self.sound_played:
            self.sound_played = True
            dashboard.points += 100
            sound.play_sfx(sound.coin)
        self.coin_animation.update()
        if self.coin_animation.timer < 45:
            if self.coin_animation.timer < 15:
                self.itemVel.y -= 0.5
                self.ItemPos.y += self.itemVel.y
            elif self.coin_animation.timer < 45:
                self.itemVel.y += 0.5
                self.ItemPos.y += self.itemVel.y
            self.screen.blit(
                self.coin_animation.image, (self.ItemPos.x + cam.x, self.ItemPos.y)
            )
        elif self.coin_animation.timer < 80:
            self.itemVel.y = -0.75
            self.ItemPos.y += self.itemVel.y
            self.drawText("100", self.ItemPos.x + 3 + cam.x, self.ItemPos.y, 8)


class Collider:
    def __init__(self, entity, level):
        self.entity = entity
        self.level = level.level
        self.levelObj = level
        self.result = []

    def checkX(self):
        if self.leftLevelBorderReached() or self.rightLevelBorderReached():
            return
        try:
            rows = [
                self.level[self.entity.getPosIndex().y],
                self.level[self.entity.getPosIndex().y + 1],
                self.level[self.entity.getPosIndex().y + 2],
            ]
        except Exception:
            return
        for row in rows:
            tiles = row[self.entity.getPosIndex().x: self.entity.getPosIndex().x + 2]
            for tile in tiles:
                if tile.rect is not None:
                    if self.entity.rect.colliderect(tile.rect):
                        if self.entity.vel.x > 0:
                            self.entity.rect.right = tile.rect.left
                            self.entity.vel.x = 0
                        if self.entity.vel.x < 0:
                            self.entity.rect.left = tile.rect.right
                            self.entity.vel.x = 0

    def checkY(self):
        self.entity.onGround = False

        try:
            rows = [
                self.level[self.entity.getPosIndex().y],
                self.level[self.entity.getPosIndex().y + 1],
                self.level[self.entity.getPosIndex().y + 2],
            ]
        except Exception:
            try:
                self.entity.gameOver()
            except Exception:
                self.entity.alive = None
            return
        for row in rows:
            tiles = row[self.entity.getPosIndex().x: self.entity.getPosIndex().x + 2]
            for tile in tiles:
                if tile.rect is not None:
                    if self.entity.rect.colliderect(tile.rect):
                        if self.entity.vel.y > 0:
                            self.entity.onGround = True
                            self.entity.rect.bottom = tile.rect.top
                            self.entity.vel.y = 0
                            # reset jump on bottom
                            if self.entity.traits is not None:
                                if "JumpTrait" in self.entity.traits:
                                    self.entity.traits["JumpTrait"].reset()
                                if "bounceTrait" in self.entity.traits:
                                    self.entity.traits["bounceTrait"].reset()
                        if self.entity.vel.y < 0:
                            self.entity.rect.top = tile.rect.bottom
                            self.entity.vel.y = 0

    def rightLevelBorderReached(self):
        if self.entity.getPosIndexAsFloat().x > self.levelObj.levelLength - 1:
            self.entity.rect.x = (self.levelObj.levelLength - 1) * 32
            self.entity.vel.x = 0
            return True

    def leftLevelBorderReached(self):
        if self.entity.rect.x < 0:
            self.entity.rect.x = 0
            self.entity.vel.x = 0
            return True


class Goomba(EntityBase):
    def __init__(self, screen, spriteColl, x, y, level, sound):
        super(Goomba, self).__init__(y, x - 1, 1.25)
        self.spriteCollection = spriteColl
        self.animation = clases.Animation(
            [
                self.spriteCollection.get("goomba-1").image,
                self.spriteCollection.get("goomba-2").image,
            ]
        )
        self.screen = screen
        self.leftrightTrait = traits.LeftRightWalkTrait(self, level)
        self.type = "Mob"
        self.dashboard = level.dashboard
        self.collision = Collider(self, level)
        self.EntityCollider = clases.EntityCollider(self)
        self.levelObj = level
        self.sound = sound
        self.textPos = clases.Vec2D(0, 0)

    def update(self, camera):
        if self.alive:
            self.applyGravity()
            self.drawGoomba(camera)
            self.leftrightTrait.update()
            self.checkEntityCollision()
        else:
            self.onDead(camera)

    def drawGoomba(self, camera):
        self.screen.blit(self.animation.image, (self.rect.x + camera.x, self.rect.y))
        self.animation.update()

    def onDead(self, camera):
        if self.timer == 0:
            self.setPointsTextStartPosition(self.rect.x + 3, self.rect.y)
        if self.timer < self.timeAfterDeath:
            self.movePointsTextUpAndDraw(camera)
            self.drawFlatGoomba(camera)
        else:
            self.alive = None
        self.timer += 0.1

    def drawFlatGoomba(self, camera):
        self.screen.blit(
            self.spriteCollection.get("goomba-flat").image,
            (self.rect.x + camera.x, self.rect.y),
        )

    def setPointsTextStartPosition(self, x, y):
        self.textPos = clases.Vec2D(x, y)

    def movePointsTextUpAndDraw(self, camera):
        self.textPos.y += -0.5
        self.dashboard.drawText("100", self.textPos.x + camera.x, self.textPos.y, 8)

    def checkEntityCollision(self):
        for ent in self.levelObj.entityList:
            collisionState = self.EntityCollider.check(ent)
            if collisionState.isColliding:
                if ent.type == "Mob":
                    self._onCollisionWithMob(ent, collisionState)

    def _onCollisionWithMob(self, mob, collisionState):
        if collisionState.isColliding and mob.alive == "shellBouncing":
            self.alive = False
            self.sound.play_sfx(self.sound.brick_bump)


class Coin(EntityBase):
    def __init__(self, screen, spriteCollection, x, y, gravity=0):
        super(Coin, self).__init__(x, y, gravity)
        self.screen = screen
        self.spriteCollection = spriteCollection
        self.animation = copy(self.spriteCollection.get("coin").animation)
        self.type = "Item"

    def update(self, cam):
        if self.alive:
            self.animation.update()
            self.screen.blit(self.animation.image, (self.rect.x + cam.x, self.rect.y))


class CoinBrick(EntityBase):
    def __init__(self, screen, spriteCollection, x, y, sound, dashboard, gravity=0):
        super(CoinBrick, self).__init__(x, y, gravity)
        self.screen = screen
        self.spriteCollection = spriteCollection
        self.image = self.spriteCollection.get("bricks").image
        self.type = "Block"
        self.triggered = False
        self.sound = sound
        self.dashboard = dashboard
        self.item = Item(spriteCollection, screen, self.rect.x, self.rect.y)

    def update(self, cam):
        if not self.alive or self.triggered:
            self.image = self.spriteCollection.get("empty").image
            self.item.spawnCoin(cam, self.sound, self.dashboard)
        self.screen.blit(
            self.spriteCollection.get("sky").image,
            (self.rect.x + cam.x, self.rect.y + 2),
        )
        self.screen.blit(self.image, (self.rect.x + cam.x, self.rect.y - 1))


class CoinBox(EntityBase):
    def __init__(self, screen, spriteCollection, x, y, sound, dashboard, gravity=0):
        super(CoinBox, self).__init__(x, y, gravity)
        self.screen = screen
        self.spriteCollection = spriteCollection
        self.animation = copy(self.spriteCollection.get("CoinBox").animation)
        self.type = "Block"
        self.triggered = False
        self.time = 0
        self.maxTime = 10
        self.sound = sound
        self.dashboard = dashboard
        self.vel = 1
        self.item = Item(spriteCollection, screen, self.rect.x, self.rect.y)

    def update(self, cam):
        if self.alive and not self.triggered:
            self.animation.update()
        else:
            self.animation.image = self.spriteCollection.get("empty").image
            self.item.spawnCoin(cam, self.sound, self.dashboard)
            if self.time < self.maxTime:
                self.time += 1
                self.rect.y -= self.vel
            else:
                if self.time < self.maxTime * 2:
                    self.time += 1
                    self.rect.y += self.vel
        self.screen.blit(
            self.spriteCollection.get("sky").image,
            (self.rect.x + cam.x, self.rect.y + 2),
        )
        self.screen.blit(self.animation.image, (self.rect.x + cam.x, self.rect.y - 1))


class Koopa(EntityBase):
    def __init__(self, screen, spriteColl, x, y, level, sound):
        super(Koopa, self).__init__(y - 1, x, 1.25)
        self.spriteCollection = spriteColl
        self.animation = clases.Animation(
            [
                self.spriteCollection.get("koopa-1").image,
                self.spriteCollection.get("koopa-2").image,
            ]
        )
        self.screen = screen
        self.leftrightTrait = traits.LeftRightWalkTrait(self, level)
        self.timer = 0
        self.timeAfterDeath = 35
        self.type = "Mob"
        self.dashboard = level.dashboard
        self.collision = Collider(self, level)
        self.EntityCollider = clases.EntityCollider(self)
        self.levelObj = level
        self.sound = sound

    def update(self, camera):
        if self.alive is True:
            self.updateAlive(camera)
            self.checkEntityCollision()
        elif self.alive == "sleeping":
            self.sleepingInShell(camera)
            self.checkEntityCollision()
        elif self.alive == "shellBouncing":
            self.shellBouncing(camera)

    def drawKoopa(self, camera):
        if self.leftrightTrait.direction == -1:
            self.screen.blit(
                self.animation.image, (self.rect.x + camera.x, self.rect.y - 32)
            )
        else:
            self.screen.blit(
                pygame.transform.flip(self.animation.image, True, False),
                (self.rect.x + camera.x, self.rect.y - 32),
            )

    def shellBouncing(self, camera):
        self.leftrightTrait.speed = 4
        self.applyGravity()
        self.animation.image = self.spriteCollection.get("koopa-hiding").image
        self.drawKoopa(camera)
        self.leftrightTrait.update()

    def sleepingInShell(self, camera):
        if self.timer < self.timeAfterDeath:
            self.screen.blit(
                self.spriteCollection.get("koopa-hiding").image,
                (self.rect.x + camera.x, self.rect.y - 32),
            )
        else:
            self.alive = True
            self.timer = 0
        self.timer += 0.1

    def updateAlive(self, camera):
        self.applyGravity()
        self.drawKoopa(camera)
        self.animation.update()
        self.leftrightTrait.update()

    def checkEntityCollision(self):
        for ent in self.levelObj.entityList:
            if ent is not self:
                collisionState = self.EntityCollider.check(ent)
                if collisionState.isColliding:
                    if ent.type == "Mob":
                        self._onCollisionWithMob(ent, collisionState)

    def _onCollisionWithMob(self, mob, collisionState):
        if collisionState.isColliding and mob.alive == "shellBouncing":
            self.alive = False
            self.sound.play_sfx(self.sound.brick_bump)


spriteCollection = clases.Sprites().spriteCollection
smallAnimation = clases.Animation(
    [
        spriteCollection["mario_run1"].image,
        spriteCollection["mario_run2"].image,
        spriteCollection["mario_run3"].image,
    ],
    spriteCollection["mario_idle"].image,
    spriteCollection["mario_jump"].image,
)
bigAnimation = clases.Animation(
    [
        spriteCollection["mario_big_run1"].image,
        spriteCollection["mario_big_run2"].image,
        spriteCollection["mario_big_run3"].image,
    ],
    spriteCollection["mario_big_idle"].image,
    spriteCollection["mario_big_jump"].image,
)


class RedMushroom(EntityBase):
    def __init__(self, screen, spriteColl, x, y, level, sound):
        super(RedMushroom, self).__init__(y, x - 1, 1.25)
        self.spriteCollection = spriteColl
        self.animation = clases.Animation(
            [
                self.spriteCollection.get("mushroom").image,
            ]
        )
        self.screen = screen
        self.leftrightTrait = traits.LeftRightWalkTrait(self, level)
        self.type = "Mob"
        self.dashboard = level.dashboard
        self.collision = Collider(self, level)
        self.EntityCollider = clases.EntityCollider(self)
        self.levelObj = level
        self.sound = sound

    def update(self, camera):
        if self.alive:
            self.applyGravity()
            self.drawRedMushroom(camera)
            self.leftrightTrait.update()
            self.checkEntityCollision()
        else:
            self.onDead(camera)

    def drawRedMushroom(self, camera):
        self.screen.blit(self.animation.image, (self.rect.x + camera.x, self.rect.y))
        self.animation.update()

    def onDead(self, camera):
        if self.timer == 0:
            self.setPointsTextStartPosition(self.rect.x + 3, self.rect.y)
        if self.timer < self.timeAfterDeath:
            self.movePointsTextUpAndDraw(camera)
        else:
            self.alive = None
        self.timer += 0.1

    def setPointsTextStartPosition(self, x, y):
        self.textPos = clases.Vec2D(x, y)

    def movePointsTextUpAndDraw(self, camera):
        self.textPos.y += -0.5
        self.dashboard.drawText("100", self.textPos.x + camera.x, self.textPos.y, 8)

    def checkEntityCollision(self):
        pass


class Mario(EntityBase):
    def __init__(self, x, y, level, screen, dashboard, sound, gravity=0.75):
        super(Mario, self).__init__(x, y, gravity)
        self.camera = clases.Camera(self.rect, self)
        self.sound = sound
        self.input = clases.Input(self)
        self.inAir = False
        self.inJump = False
        self.powerUpState = 0
        self.invincibilityFrames = 0
        self.traits = {
            "jumpTrait": traits.JumpTrait(self),
            "goTrait": traits.GoTrait(smallAnimation, screen, self.camera, self),
            "bounceTrait": traits.bounceTrait(self),
        }

        self.levelObj = level
        self.collision = Collider(self, level)
        self.screen = screen
        self.EntityCollider = clases.EntityCollider(self)
        self.dashboard = dashboard
        self.restart = False
        self.pause = False
        self.pauseObj = clases.Pause(screen, self, dashboard)

    def update(self):
        if self.invincibilityFrames > 0:
            self.invincibilityFrames -= 1
        self.updateTraits()
        self.moveMario()
        self.camera.move()
        self.applyGravity()
        self.checkEntityCollision()
        self.input.checkForInput()

    def moveMario(self):
        self.rect.y += self.vel.y
        self.collision.checkY()
        self.rect.x += self.vel.x
        self.collision.checkX()

    def checkEntityCollision(self):
        for ent in self.levelObj.entityList:
            collisionState = self.EntityCollider.check(ent)
            if collisionState.isColliding:
                if ent.type == "Item":
                    self._onCollisionWithItem(ent)
                elif ent.type == "Block":
                    self._onCollisionWithBlock(ent)
                elif ent.type == "Mob":
                    self._onCollisionWithMob(ent, collisionState)

    def _onCollisionWithItem(self, item):
        self.levelObj.entityList.remove(item)
        self.dashboard.points += 100
        self.dashboard.coins += 1
        self.sound.play_sfx(self.sound.coin)

    def _onCollisionWithBlock(self, block):
        if not block.triggered:
            self.dashboard.coins += 1
            self.sound.play_sfx(self.sound.bump)
        block.triggered = True

    def _onCollisionWithMob(self, mob, collisionState):
        if isinstance(mob, RedMushroom) and mob.alive:
            self.powerup(1)
            self.killEntity(mob)
            self.sound.play_sfx(self.sound.powerup)
        elif collisionState.isTop and (mob.alive or mob.alive == "shellBouncing"):
            self.sound.play_sfx(self.sound.stomp)
            self.rect.bottom = mob.rect.top
            self.bounce()
            self.killEntity(mob)
        elif collisionState.isTop and mob.alive == "sleeping":
            self.sound.play_sfx(self.sound.stomp)
            self.rect.bottom = mob.rect.top
            mob.timer = 0
            self.bounce()
            mob.alive = False
        elif collisionState.isColliding and mob.alive == "sleeping":
            if mob.rect.x < self.rect.x:
                mob.leftrightTrait.direction = -1
                mob.rect.x += -5
                self.sound.play_sfx(self.sound.kick)
            else:
                mob.rect.x += 5
                mob.leftrightTrait.direction = 1
                self.sound.play_sfx(self.sound.kick)
            mob.alive = "shellBouncing"
        elif collisionState.isColliding and mob.alive and not self.invincibilityFrames:
            if self.powerUpState == 0:
                self.gameOver()
            elif self.powerUpState == 1:
                self.powerUpState = 0
                self.traits['goTrait'].updateAnimation(smallAnimation)
                x, y = self.rect.x, self.rect.y
                self.rect = pygame.Rect(x, y + 32, 32, 32)
                self.invincibilityFrames = 60
                self.sound.play_sfx(self.sound.pipe)

    def bounce(self):
        self.traits["bounceTrait"].jump = True

    def killEntity(self, ent):
        if ent.__class__.__name__ != "Koopa":
            ent.alive = False
        else:
            ent.timer = 0
            ent.leftrightTrait.speed = 1
            ent.alive = "sleeping"
        self.dashboard.points += 100

    def gameOver(self):
        srf = pygame.Surface((640, 480))
        srf.set_colorkey((255, 255, 255), pygame.RLEACCEL)
        srf.set_alpha(128)
        self.sound.music_channel.stop()
        self.sound.music_channel.play(self.sound.death)

        for i in range(500, 20, -2):
            srf.fill((0, 0, 0))
            pygame.draw.circle(
                srf,
                (255, 255, 255),
                (int(self.camera.x + self.rect.x) + 16, self.rect.y + 16),
                i,
            )
            self.screen.blit(srf, (0, 0))
            pygame.display.update()
            self.input.checkForInput()
        while self.sound.music_channel.get_busy():
            pygame.display.update()
            self.input.checkForInput()
        self.restart = True

    def getPos(self):
        return self.camera.x + self.rect.x, self.rect.y

    def setPos(self, x, y):
        self.rect.x = x
        self.rect.y = y

    def powerup(self, powerupID):
        if self.powerUpState == 0:
            if powerupID == 1:
                self.powerUpState = 1
                self.traits['goTrait'].updateAnimation(bigAnimation)
                self.rect = pygame.Rect(self.rect.x, self.rect.y - 32, 32, 64)
                self.invincibilityFrames = 20


class RandomBox(EntityBase):
    def __init__(self, screen, spriteCollection, x, y, item, sound, dashboard, level, gravity=0):
        super(RandomBox, self).__init__(x, y, gravity)
        self.screen = screen
        self.spriteCollection = spriteCollection
        self.animation = copy(self.spriteCollection.get("CoinBox").animation)
        self.type = "Block"
        self.triggered = False
        self.time = 0
        self.maxTime = 10
        self.sound = sound
        self.dashboard = dashboard
        self.vel = 1
        self.item = item
        self.level = level

    def update(self, cam):
        if self.alive and not self.triggered:
            self.animation.update()
        else:
            self.animation.image = self.spriteCollection.get("empty").image
            if self.item == 'RedMushroom':
                self.level.addRedMushroom(self.rect.y // 32 - 1, self.rect.x // 32)
                self.sound.play_sfx(self.sound.powerup_appear)
            self.item = None
            if self.time < self.maxTime:
                self.time += 1
                self.rect.y -= self.vel
            else:
                if self.time < self.maxTime * 2:
                    self.time += 1
                    self.rect.y += self.vel
        self.screen.blit(
            self.spriteCollection.get("sky").image,
            (self.rect.x + cam.x, self.rect.y + 2),
        )
        self.screen.blit(self.animation.image, (self.rect.x + cam.x, self.rect.y - 1))
