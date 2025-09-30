// Set the date we're counting down to in UTC.
// Midnight EDT (00:00:00) on 2025-10-01 is 04:00:00 UTC on the same date.
var countDownDate = new Date("2025-10-01T04:00:00Z").getTime();

// Update the count down every 1 second
var x = setInterval(function() {

  // Get today's date and time
  var now = new Date().getTime();

  // Find the distance between now and the count down date
  var distance = countDownDate - now;

  // Time calculations for days, hours, minutes and seconds
  var days = Math.floor(distance / (1000 * 60 * 60 * 24));
  var hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
  var minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
  var seconds = Math.floor((distance % (1000 * 60)) / 1000);

  // Variable to hold the final display string
  let timerOutput = ""; 

  // Check if the count down is finished first
  if (distance < 0) {
    clearInterval(x);
    timerOutput = "EVENT ONGOING";
  } 
  // Else, determine the display format based on remaining time
  else if (days > 0) {
    // Show full format (Days, Hours, Minutes, Seconds)
    timerOutput = days + " days, " + hours + " hours, " + minutes + " minutes, " + seconds + " seconds";
  } else if (hours > 0) {
    // Show reduced format (Hours, Minutes, Seconds)
    timerOutput = hours + " hours, " + minutes + " minutes, " + seconds + " seconds";
  } else if (minutes > 0) {
    // Show final minute format (Minutes, Seconds)
    timerOutput = minutes + " minutes, " + seconds + " seconds";
  } else {
    // Show final seconds format (Seconds)
    // This will run when days, hours, and minutes are all 0
    timerOutput = seconds + " seconds";
  }
  
  // Display the result in the element with id="timer"
  document.getElementById("timer").innerHTML = timerOutput;
  
}, 1000);