import '../css/Home/BookingSection.css';
import bookingCar from '../assets/booking-car.jpeg';
import { Phone, Calendar, MapPin, Users, Clock, User } from 'lucide-react';

export default function BookingSection() {
    return (
        <section className="booking" id="contact">
            <div className="booking__left">
                <p className="booking__label">🚖 TAXI BOOKING</p>
                <h2>
                    <span>Book Your Taxi</span><br />
                    <strong>On Online</strong>
                </h2>
                <p className="booking__desc">
                    It is a long established fact that a reader will be distracted by the readable content of a page when looking at its layout...
                </p>

                <form className="booking__form">
                    <div className="booking__row">
                        <div className="booking__input">
                            <input type="text" placeholder="Your name" />
                            <User size={16} />
                        </div>
                    </div>

                    <div className="booking__row">
                        <div className="booking__input">
                            <input type="text" placeholder="Phone Number" />
                            <Phone size={16} />
                        </div>
                        <div className="booking__input">
                            <select className='booking__passenger-select'>
                                <option>Passengers</option>
                                <option>1</option>
                                <option>2</option>
                                <option>3+</option>
                            </select>
                        </div>
                    </div>

                    <div className="booking__row">
                        <div className="booking__input">
                            <input type="text" placeholder="Start Destination" />
                            <MapPin size={16} />
                        </div>
                        <div className="booking__input">
                            <input type="text" placeholder="End Destination" />
                            <MapPin size={16} />
                        </div>
                    </div>

                    <div className="booking__row">
                        <div className="booking__input">
                            <input type="date" />
                            <Calendar size={16} />
                        </div>
                        <div className="booking__input">
                            <input type="time" />
                            <Clock size={16} />
                        </div>
                    </div>

                    <button type="submit" className="booking__submit">BOOK NOW</button>
                </form>

            </div>

            <div className="booking__right">
                <img src={bookingCar} alt="Booking Taxi" />
            </div>
        </section>
    );
}
