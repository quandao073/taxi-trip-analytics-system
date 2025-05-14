import '../css/Home/AboutSection.css';
import taxiImg1 from '../assets/taxi1.jpeg';
import taxiImg2 from '../assets/taxi2.jpeg';
import { BadgePercent, CarTaxiFront } from 'lucide-react';

export default function HomeAbout() {
  return (
    <section className="about" id="aboutus">
      <div className="about__cards">
        <div className="about__card" style={{ backgroundImage: `url(${taxiImg1})` }}>
          <div className="about__card-info">
            <BadgePercent className="about__icon" />
            <h3>26+</h3>
            <p>Years Experience</p>
          </div>
        </div>
        <div className="about__card" style={{ backgroundImage: `url(${taxiImg2})` }}>
          <div className="about__card-info">
            <CarTaxiFront className="about__icon" />
            <h3>32k+</h3>
            <p>Special Vehicles</p>
          </div>
        </div>
      </div>

      <div className="about__content">
        <p className="about__label">🚗 ABOUT OUR COMPANY</p>
        <h2>Professional and Dedicated</h2>
        <h3>Online Taxi Service</h3>
        <p className="about__desc">
          It is a long established fact that a reader will be distracted by the readable content of a page when looking at its layout...
        </p>
        <button className="about__btn">DISCOVER MORE</button>
      </div>
    </section>
  );
}
