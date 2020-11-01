console.log("Hello I am in tweet.js file");
// console.log(tweets, user);

// function tweepy(tweets, user) {
// console.log("Inside tweepy function");
// for(i in tweets){
//     console.log();
// }
console.log(users[1]);
let post = document.getElementById("tweetpost");
html = ""
var i;
for(i in tweets){
    var j, k;
    for(j in user){
        if(j[0] == i[1]){
            k = j;
            break;
        }
    }
    html += `<div class="userimg"><img src="static/images/homaj logo.png"/>
    </div>
    <div class="username"><p class="name">${j[1]}</p>
    </div>
    <p class="time">${i[3]}</p>
    <p class="quotes">
        ${i[2]}	
    </p>
    <div class="likedislike">
        <p class="like">
            <span class="nooflike" id="like1">0 </span> likes &nbsp <span class="noofdislike" id="dislike1">0 </span> dislikes
        </p>
        <p class="likedisbttn">
            <span id="thumbsup1" class="fa fa-thumbs-up" onclick="increase('like1','dislike1','thumbsup1','thumbsdown1');"></span> <span id="thumbsdown1" class="fa fa-thumbs-down" onclick="decrease('like1','dislike1','thumbsup1','thumbsdown1');"></span>
        </p>
    </div> `
}

document.getElementById("tweetpost").innerHTML = html;
