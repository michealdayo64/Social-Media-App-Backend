const APP_ID = sessionStorage.getItem("appid");
const TOKEN = sessionStorage.getItem("token");
const CHANNEL = sessionStorage.getItem("room");
let UID = Number(sessionStorage.getItem("UID"));
let NAME = sessionStorage.getItem("name");

const client = AgoraRTC.createClient({ mode: "rtc", codec: "vp8" });

let localTracks = [];
let remoteUsers = {};

let joinAndDisplayLocalStream = async () => {
  document.getElementById("room-name").innerHTML = `Room name: ${CHANNEL}`;

  client.on("user-published", handleUserJoin);
  client.on("user-left", handleUserLetf);

  try {
    await client.join(APP_ID, CHANNEL, TOKEN, UID);
  } catch (e) {
    console.log(e);
    window.open("/", "_self");
  }

  let member = await createMember();

  localTracks = await AgoraRTC.createMicrophoneAndCameraTracks();
  let player = `<div  class="video-container" id="user-container-${UID}">
                     <div class="video-player" id="user-${UID}">${member.name}</div>
                     <div class="username-wrapper"><span class="user-name">name:</span></div>
                  </div>`;

  document
    .getElementById("video-streams")
    .insertAdjacentHTML("beforeend", player);
  localTracks[1].play(`user-${UID}`);
  await client.publish([localTracks[0], localTracks[1]]);
};

// HANDLE USER JOINED
let handleUserJoin = async (user, mediaType) => {
  console.log("User joined", user);
  remoteUsers[user.uid] = user;
  await client.subscribe(user, mediaType);

  if (mediaType === "video") {
    let player = document.getElementById(`user-container-${user.uid}`);
    if (player !== null) {
      player.remove();
    }

    let member = await getMember(user);
    player = `<div  class="video-container" id="user-container-${user.uid}">
                       <div class="video-player" id="user-${user.uid}">${member.name}</div>
                       <div class="username-wrapper"><span class="user-name">name:</span></div>
                    </div>`;

    document
      .getElementById("video-streams")
      .insertAdjacentHTML("beforeend", player);
    user.videoTrack.play(`user-${user.uid}`);
  }

  if (mediaType === "audio") {
    user.audioTrack.play();
  }
};

// HANDLE USER LEFT
let handleUserLetf = (user) => {
  delete remoteUsers[user.uid];
  document.getElementById(`user-container-${user.uid}`).remove();
};

// USER LETF BUTTON
let leaveAndRemoveLocalStream = async () => {
  for (let i = 0; localTracks.length > i; i++) {
    localTracks[i].stop;
    localTracks[i].close;
  }
  await client.leave();
  //await deleteMember();
  window.open("http://127.0.0.1:8000/home/", "_self");
};

// USER ON AND OFF CAMERA
let toggleCamera = async (e) => {
  console.log("TOGGLE CAMERA TRIGGERED");
  if (localTracks[1].muted) {
    await localTracks[1].setMuted(false);
    e.target.style.backgroundColor = "#fff";
  } else {
    await localTracks[1].setMuted(true);
    e.target.style.backgroundColor = "rgb(255, 80, 80, 1)";
  }
};

// USER ON AND OFF MICROPHONE
let toggleMic = async (e) => {
  console.log("TOGGLE MIC TRIGGERED");
  if (localTracks[0].muted) {
    await localTracks[0].setMuted(false);
    e.target.style.backgroundColor = "#fff";
  } else {
    await localTracks[0].setMuted(true);
    e.target.style.backgroundColor = "rgb(255, 80, 80, 1)";
  }
};

let createMember = async () => {
  let host = window.location.origin;
  let response = await fetch(`${host}/group/create-member/`, {
    method: "POST",
    headers: {
      "X-CSRFToken": csrftoken,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ username: NAME, UID: UID, room_name: CHANNEL }),
  });
  let member = response.json();
  return member;
};

let getMember = async (user) => {
  let host = window.location.origin;
  let response = await fetch(
    `${host}/group/get-member/?UID=${user.uid}&room_name=${CHANNEL}`
  );
  let member = response.json();
  return member;
};

joinAndDisplayLocalStream();

document
  .getElementById("leave-btn")
  .addEventListener("click", leaveAndRemoveLocalStream);
document.getElementById("camera-btn").addEventListener("click", toggleCamera);
document.getElementById("mic-btn").addEventListener("click", toggleMic);
