(function() {
    // Set the date we're counting down to in UTC.
    const countDownDate = new Date("2026-10-11T04:00:00Z").getTime();

    // Update the count down every 1 second
    const x = setInterval(function() {

      // Get today's date and time
      const now = new Date().getTime();

      // Find the distance between now and the count down date
      const distance = countDownDate - now;

      // Time calculations
      const days = Math.floor(distance / (1000 * 60 * 60 * 24));
      const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
      const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
      const seconds = Math.floor((distance % (1000 * 60)) / 1000);

      let timerOutput = ""; 

      if (distance < 0) {
        clearInterval(x);
        timerOutput = "EVENT ONGOING";
      } 
      else if (days > 0) {
        timerOutput = days + " days, " + hours + " hours, " + minutes + " minutes, " + seconds + " seconds";
      } else if (hours > 0) {
        timerOutput = hours + " hours, " + minutes + " minutes, " + seconds + " seconds";
      } else if (minutes > 0) {
        timerOutput = minutes + " minutes, " + seconds + " seconds";
      } else {
        timerOutput = seconds + " seconds";
      }
      
      document.getElementById("gvtimer").innerHTML = timerOutput;
      
    }, 1000);
})();