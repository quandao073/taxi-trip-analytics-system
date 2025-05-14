import '../css/Home/TaxiCollection.css';
import taxi1 from '../assets/taxi-basic.png';
import taxi2 from '../assets/taxi-standard.png';
import taxi3 from '../assets/taxi-luxury.png';

const taxis = [
  {
    name: 'BASIC TAXI',
    price: '$0.47/km',
    image: taxi1,
    features: [
      ['Initial Charge:', '$2.30'],
      ['Up To 50 Kms:', '$1.50'],
      ['Additional Kilos:', '$0.80'],
      ['Per Stop Traffic:', '$0.3'],
      ['Capacity:', '4'],
      ['Air Conditioner:', 'Yes']
    ]
  },
  {
    name: 'STANDARD TAXI',
    price: '$0.95/km',
    image: taxi2,
    features: [
      ['Initial Charge:', '$3.20'],
      ['Up To 50 Kms:', '$2.10'],
      ['Additional Kilos:', '$0.90'],
      ['Per Stop Traffic:', '$0.5'],
      ['Capacity:', '4'],
      ['Air Conditioner:', 'Yes']
    ]
  },
  {
    name: 'LUXURIOUS TAXI',
    price: '$1.85/km',
    image: taxi3,
    features: [
      ['Initial Charge:', '$5.68'],
      ['Up To 50 Kms:', '$2.60'],
      ['Additional Kilos:', '$1.20'],
      ['Per Stop Traffic:', '$0.8'],
      ['Capacity:', '2'],
      ['Air Conditioner:', 'Yes']
    ]
  }
];

export default function TaxiCollection() {
  return (
    <section className="taxi-section" id="taxi">
      <div className="taxi-header">
        <p className="taxi-label">OUR TAXI</p>
        <h2>Choose Our Taxi</h2>
        <h3>Collection</h3>
        <p className="taxi-desc">
          It is a long established fact that a reader will be distracted by the readable content of a page...
        </p>
      </div>

      <div className="taxi-cards">
        {taxis.map((taxi, idx) => (
          <div className="taxi-card" key={idx}>
            <img src={taxi.image} alt={taxi.name} />
            <h4>{taxi.name}</h4>
            <span className="taxi-price">{taxi.price}</span>
            <ul className="taxi-features">
              {taxi.features.map(([label, value], i) => (
                <li key={i}>
                  <span>{label}</span>
                  <span>{value}</span>
                </li>
              ))}
            </ul>
            <button className="taxi-book">BOOK NOW</button>
          </div>
        ))}
      </div>
    </section>
  );
}
