import '../css/Home/ServiceSection.css';
import service1 from '../assets/service-city.jpeg';
import service2 from '../assets/service-booking.jpeg';
import service3 from '../assets/service-airport.jpeg';

const services = [
  {
    image: service1,
    title: 'Rapid city Transfer',
    desc: 'It is a long established fact that a reader will be distracted by the readable content of a page',
  },
  {
    image: service2,
    title: 'Online Booking',
    desc: 'It is a long established fact that a reader will be distracted by the readable content of a page',
  },
  {
    image: service3,
    title: 'Airport Transport',
    desc: 'It is a long established fact that a reader will be distracted by the readable content of a page',
  },
];

export default function ServiceSection() {
  return (
    <section className="services" id="services">
      <div className="services__header">
        <p className="services__label">OUR SERVICE</p>
        <h2>Best Taxi Service</h2>
        <h3>For Your Town</h3>
        <p className="services__desc">
          It is a long established fact that a reader will be distracted by the readable content of a page...
        </p>
      </div>

      <div className="services__cards">
        {services.map((service, idx) => (
          <div className="services__card" key={idx}>
            <img src={service.image} alt={service.title} />
            <div className="services__info">
              <h4>{service.title}</h4>
              <p>{service.desc}</p>
              <a href="#" className="services__link">Learn More →</a>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
