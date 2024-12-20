import React, { useEffect } from 'react';
import './StarryBackground.css';

const StarryBackground = () => {
  useEffect(() => {
    const init = () => {
      const style = ["style1", "style2", "style3", "style4"];
      const tam = ["tam1", "tam1", "tam1", "tam2", "tam3"];
      const opacity = ["opacity1", "opacity1", "opacity1", "opacity2", "opacity2", "opacity3"];

      function getRandomArbitrary(min, max) {
        return Math.floor(Math.random() * (max - min)) + min;
      }

      let estrela = "";
      const qtdeEstrelas = 250;
      const noite = document.querySelector(".constelacao");
      const widthWindow = window.innerWidth;
      const heightWindow = window.innerHeight;

      for (let i = 0; i < qtdeEstrelas; i++) {
        estrela += `<span class='estrela ${style[getRandomArbitrary(0, 4)]} ${opacity[getRandomArbitrary(0, 6)]} ${tam[getRandomArbitrary(0, 5)]}' style='animation-delay: .${getRandomArbitrary(0, 9)}s; left: ${getRandomArbitrary(0, widthWindow)}px; top: ${getRandomArbitrary(0, heightWindow)}px;'></span>`;
      }

      noite.innerHTML = estrela;

      let numeroAleatorio = 5000;

      const carregarMeteoro = () => {
        setTimeout(carregarMeteoro, numeroAleatorio);
        numeroAleatorio = getRandomArbitrary(5000, 10000);
        const meteoro = `<div class='meteoro ${style[getRandomArbitrary(0, 4)]}'></div>`;
        document.getElementsByClassName('chuvaMeteoro')[0].innerHTML = meteoro;
        setTimeout(() => {
          document.getElementsByClassName('chuvaMeteoro')[0].innerHTML = "";
        }, 1000);
      };

      setTimeout(() => {
        carregarMeteoro();
      }, numeroAleatorio);
    };

    init();
  }, []);

  return (
    <>
      <div className="noite"></div>
      <div className="constelacao"></div>
      <div className="chuvaMeteoro"></div>
    </>
  );
};

export default StarryBackground;
