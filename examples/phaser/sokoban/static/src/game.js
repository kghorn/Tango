var gameOptions = {
    tileSize: 40,
    gameWidth: 320,
    gameHeight: 320,
    gameSpeed: 1
}

function deepCopy(obj){
    return JSON.parse(JSON.stringify(obj));
}

var level1 = [
    [1,1,1,1,1,1,1,1],
    [1,0,0,0,0,0,2,1],
    [1,0,0,0,1,1,1,1],
    [1,1,0,0,1,1,1,1],
    [1,1,4,0,0,0,0,1],
    [1,1,0,0,1,3,0,1],
    [1,1,1,1,1,0,0,1],
    [1,1,1,1,1,1,1,1]
];

var level2 = [
    [1,1,1,1,1,1,1,1],
    [1,0,0,1,1,1,1,1],
    [1,0,0,1,1,1,1,1],
    [1,0,0,0,0,0,0,1],
    [1,1,4,2,1,3,0,1],
    [1,0,0,0,1,0,0,1],
    [1,0,0,0,1,1,1,1],
    [1,1,1,1,1,1,1,1]
];

var stuck1 = [
    [0,0,0,0,0,0,0,0],
    [0,1,0,0,0,0,0,0],
    [0,1,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,1,0],
    [0,0,1,1,0,0,1,0],
    [0,0,0,0,0,1,1,0],
    [0,0,0,0,0,0,0,0]
];

var stuck2 = [
    [0,0,0,0,0,0,0,0],
    [0,1,1,0,0,0,0,0],
    [0,1,0,0,0,0,0,0],
    [0,1,0,0,0,0,1,0],
    [0,0,0,0,0,0,1,0],
    [0,1,0,0,0,1,1,0],
    [0,1,1,1,0,0,0,0],
    [0,0,0,0,0,0,0,0]
];
 
var level_start = deepCopy(level1);
var level = deepCopy(level_start);
var stuck = deepCopy(stuck1);

var EMPTY = 0;
var WALL = 1;
var SPOT = 2;
var CRATE = 3;
var PLAYER = 4;
var CRATE_ON_SPOT = 5;
var PLAYER_ON_SPOT = 6;

function returnFirstItemLoc(itemID) {
    for(let i=0; i<level.length; i++){
        for(let j=0; j<level[0].length; j++){
            if(level[i][j] == itemID){
                return [i,j];
            }
        }
    }
    return [-1,-1]
}

var [spot_i,spot_j] = returnFirstItemLoc(SPOT);

var PUSH_REWARD = 1.0;
var LEVEL_COMPLETE_REWARD = 100.0;
var WALL_BUMP_PENALTY = -.001;

var actionCount = 0;
 
window.onload = function(){
    var gameConfig = {
        type: Phaser.CANVAS, //Phaser.HEADLESS, //Phaser.CANVAS,
        width: gameOptions.gameWidth,
        height: gameOptions.gameHeight,
        scene: [playGame]
    };
    var game = new Phaser.Game(gameConfig);
    // resize();
    // window.addEventListener("resize", resize, false);

    var ws = new WebSocket("ws://localhost:8000/game/ws");
    ws.onopen = function() {
        console.log("Received connection");
    };
    ws.onmessage = function(raw_msg) {
        console.log(raw_msg);
        msg = JSON.parse(raw_msg.data);
        
        switch(msg.type){
            case "action": tango_action_start(msg); break;
            case "reset": tango_reset(msg); break;
            case "close": tango_close(msg); break;
        }
    }
    window.ws = ws;
}
function tango_action_start(msg){
    playGame.moveByAction(msg.action);
    actionCount += 1
}
function tango_action_end(action_outcome_reward){
    if(level[spot_i][spot_j] == CRATE_ON_SPOT){ // successful episode
        var response = {
            "observation" : level,
            "reward" : LEVEL_COMPLETE_REWARD + action_outcome_reward,
            "terminated" : true,
            "truncated" : false,
            "info" : {}
        };
    }
    else if(playGame.cantWin()){ // box is stuck
        var response = {
            "observation" : level,
            "reward" : 0.0, // no reward for failure
            "terminated" : true,
            "truncated" : false,
            "info" : {}
        };
    }
    else if(actionCount>100){ // took too long
        var response = {
            "observation" : level,
            "reward" : 0.0 + action_outcome_reward,
            "terminated" : false,
            "truncated" : true,
            "info" : {}
        };
    }
    else{
        var response = {
            "observation" : level,
            "reward" : 0.0 + action_outcome_reward,
            "terminated" : false,
            "truncated" : false,
            "info" : {}
        };
    }
    window.ws.send(JSON.stringify(response));
}
function tango_reset(msg){
    playGame.reset();
    console.log(JSON.stringify({"observation":level,"info":{}}));
    window.ws.send(JSON.stringify({"observation":level,"info":{}}));
}
function tango_close(msg){
    console.log("Close requested");
    window.ws.send(JSON.stringify({"info":"closed"}));
}

class PlayGame extends Phaser.Scene {
    initialize(){
        Phaser.Scene.call(this, {key: "PlayGame"});
    }
    preload(){
        this.load.spritesheet("tiles", "img/tiles.png", {
            frameWidth: gameOptions.tileSize,
            frameHeight: gameOptions.tileSize
        });
    }
    create(){
        this.crates = [];
        this.drawLevel();
        this.input.on("pointerup", this.endSwipe, this);
    }
    drawLevel(){
        this.crates.length = 0;
        for(var i = 0; i < level.length; i++){
            this.crates[i] = [];
            for(var j = 0; j < level[i].length; j++){
                this.crates[i][j] = null;
                switch(level[i][j]){
                    case PLAYER:
                    case PLAYER + SPOT:
                        this.player = this.add.sprite(gameOptions.tileSize * j, gameOptions.tileSize * i, "tiles", level[i][j]);
                        this.player.posX = j;
                        this.player.posY = i;
                        this.player.depth = 1
                        this.player.setOrigin(0);
                        var tile = this.add.sprite(gameOptions.tileSize * j, gameOptions.tileSize * i, "tiles", level[i][j] - PLAYER);
                        tile.setOrigin(0);
                        tile.depth = 0;
                        break;
                    case CRATE:
                    case CRATE + SPOT:
                        this.crates[i][j] = this.add.sprite(gameOptions.tileSize * j, gameOptions.tileSize * i, "tiles", level[i][j]);
                        this.crates[i][j].setOrigin(0);
                        this.crates[i][j].depth = 1
                        var tile = this.add.sprite(gameOptions.tileSize * j, gameOptions.tileSize * i, "tiles", level[i][j] - CRATE);
                        tile.setOrigin(0);
                        break;
                    default:
                        var tile = this.add.sprite(gameOptions.tileSize * j, gameOptions.tileSize * i, "tiles", level[i][j]);
                        tile.setOrigin(0);
                }
            }
        }
    }
    reset() {
        level = deepCopy(level_start);
        actionCount = 0;
        let allSprites = this.children.list.filter(x => x instanceof Phaser.GameObjects.Sprite);
        allSprites.forEach(x => x.destroy());
        this.drawLevel()
    }
    boxInCorner() {
        var [i,j] = returnFirstItemLoc(CRATE);
        if(i==-1){
            return false;
        }
        var upperLeft  = (level[i-1][j]==WALL) & (level[i][j-1]==WALL);
        var upperRight = (level[i-1][j]==WALL) & (level[i][j+1]==WALL);
        var lowerLeft  = (level[i+1][j]==WALL) & (level[i][j-1]==WALL);
        var lowerRight = (level[i+1][j]==WALL) & (level[i][j+1]==WALL);
        return upperLeft | upperRight | lowerLeft | lowerRight;
    }
    cantWin(){
        var [i,j] = returnFirstItemLoc(CRATE);
        if(i!=-1){
            return stuck[i][j];
        }
        else{
            return false;
        }
    }
    boxProximityReward(){
        return 0.0;

        //return 0.001 * ((level.length+level[0].length-2) - this.boxManhattanDistanceToPlayer());

        // if(this.boxManhattanDistance()<=1){
        //     return 0.001;
        // }
        // else{
        //     return 0.0;
        // }
    }
    boxManhattanDistanceToPlayer(){
        var [player_i,player_j] = returnFirstItemLoc(PLAYER);
        if(player_i==-1){
            var [player_i,player_j] = returnFirstItemLoc(PLAYER_ON_SPOT);
        }
        var [box_i,box_j] = returnFirstItemLoc(CRATE);
        if(box_i==-1){
            var [box_i,box_j] = returnFirstItemLoc(CRATE_ON_SPOT);
        }
        return Math.abs(player_i-box_i)+Math.abs(player_j-box_j);
    }
    boxManhattanDistanceToGoal(){
        var [player_i,player_j] = returnFirstItemLoc(PLAYER);
        if(player_i==-1){
            var [player_i,player_j] = returnFirstItemLoc(PLAYER_ON_SPOT);
        }
        var [box_i,box_j] = returnFirstItemLoc(CRATE);
        if(box_i==-1){
            var [box_i,box_j] = returnFirstItemLoc(CRATE_ON_SPOT);
        }
        return Math.abs(player_i-box_i)+Math.abs(player_j-box_j);
    }
    endSwipe(e) {
        var swipeTime = e.upTime - e.downTime;
        var swipe = new Phaser.Geom.Point(e.upX - e.downX, e.upY - e.downY);
        var swipeMagnitude = Phaser.Geom.Point.GetMagnitude(swipe);
        var swipeNormal = new Phaser.Geom.Point(swipe.x / swipeMagnitude, swipe.y / swipeMagnitude);
        if(swipeMagnitude > 20 && swipeTime < 1000 && (Math.abs(swipeNormal.y) > 0.8 || Math.abs(swipeNormal.x) > 0.8)) {
            if(swipeNormal.x > 0.8) {
                this.checkMove(1, 0);
            }
            if(swipeNormal.x < -0.8) {
                this.checkMove(-1, 0);
            }
            if(swipeNormal.y > 0.8) {
                this.checkMove(0, 1);
            }
            if(swipeNormal.y < -0.8) {
                this.checkMove(0, -1);
            }
        }
    }
    moveByAction(action) {
        if(action==0){
            this.checkMove(0, 1);
        }
        else if (action==1){
            this.checkMove(1, 0);
        }
        else if (action==2){
            this.checkMove(0, -1);
        }
        else if (action==3){
            this.checkMove(-1, 0);
        }
    }
    checkMove(deltaX, deltaY){
        if(this.isWalkable(this.player.posX + deltaX, this.player.posY + deltaY)){
            this.movePlayer(deltaX, deltaY, 0);
            return;
        }
        else if(this.isCrate(this.player.posX + deltaX, this.player.posY + deltaY)){
            if(this.isWalkable(this.player.posX + 2 * deltaX, this.player.posY + 2 * deltaY)){
                
                this.moveCrate(deltaX, deltaY);
                this.movePlayer(deltaX, deltaY, PUSH_REWARD);
                return;
            }
        }
        window.tango_action_end(WALL_BUMP_PENALTY); // if the player doesn't move, then manually declare the action over
    }
    isWalkable(posX, posY){
       return level[posY][posX] == EMPTY || level[posY][posX] == SPOT;
    }
    isCrate(posX, posY){
        return level[posY][posX] == CRATE || level[posY][posX] == CRATE + SPOT;
    }
    movePlayer(deltaX, deltaY, reward=0){
        var playerTween = this.tweens.add({
            targets: this.player,
            x: this.player.x + deltaX * gameOptions.tileSize,
            y: this.player.y + deltaY * gameOptions.tileSize,
            duration: gameOptions.gameSpeed,
            onComplete: function(tween, target, player){
                player.setFrame(level[player.posY][player.posX]);
                window.tango_action_end(reward);
            },
            onCompleteParams: [this.player]
        });
        level[this.player.posY][this.player.posX] -= PLAYER;
        this.player.posX += deltaX;
        this.player.posY += deltaY;
        level[this.player.posY][this.player.posX] += PLAYER;
    }
    moveCrate(deltaX, deltaY){
        var crateTween = this.tweens.add({
            targets: this.crates[this.player.posY + deltaY][this.player.posX + deltaX],
            x: this.crates[this.player.posY + deltaY][this.player.posX + deltaX].x + deltaX * gameOptions.tileSize,
            y: this.crates[this.player.posY + deltaY][this.player.posX + deltaX].y + deltaY * gameOptions.tileSize,
            duration: gameOptions.gameSpeed,
            onComplete: function(tween, target, crate, player){
                crate.setFrame(level[player.posY + deltaY][player.posX + deltaX]);
            },
            onCompleteParams: [this.crates[this.player.posY + deltaY][this.player.posX + deltaX], this.player]
        })
        this.crates[this.player.posY + 2 * deltaY][this.player.posX + 2 * deltaX] = this.crates[this.player.posY + deltaY][this.player.posX + deltaX];
        this.crates[this.player.posY + deltaY][this.player.posX + deltaX] = null;
        level[this.player.posY + deltaY][this.player.posX + deltaX] -= CRATE;
        level[this.player.posY + 2 * deltaY][this.player.posX + 2 * deltaX] += CRATE;
    }
}

var playGame = new PlayGame()

function resize() {
    var canvas = document.querySelector("canvas");
    var windowWidth = window.innerWidth;
    var windowHeight = window.innerHeight;
    var windowRatio = windowWidth / windowHeight;
    var gameRatio = game.config.width / game.config.height;
    if(windowRatio < gameRatio){
        canvas.style.width = windowWidth + "px";
        canvas.style.height = (windowWidth / gameRatio) + "px";
    }
    else{
        canvas.style.width = (windowHeight * gameRatio) + "px";
        canvas.style.height = windowHeight + "px";
    }
}