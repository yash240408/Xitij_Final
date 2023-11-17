const scroll = new LocomotiveScroll({
  el: document.querySelector(".main"),
  smooth: true,
});



gsap.from("#page1 h1", {
  y: 90,
  opacity: 0,
  delay: 0.3,
  duration: 0.9,
  stagger: 0.2,
});

