import '../css/Footer.css';
import logo from '../assets/logo.png';
import qr from '../assets/qr-code.png';
import googlePlay from '../assets/google-play.png';
import appStore from '../assets/app-store.png';
import { Mail, MapPin, Phone, Facebook, Linkedin, Youtube, Instagram, Send } from 'lucide-react';

export default function Footer() {
  return (
    <footer className="footer">
      <div className="footer__top">
        {/* Cột 1 */}
        <div className="footer__col">
          <img src={logo} alt="Trocar Logo" className="footer__logo" />
          <p className="footer__desc">
            It has a more-or-less normal distribution of letters, as opposed to using.
          </p>
          <div className="footer__apps">
            <img src={qr} alt="QR" />
            <div>
              <img src={googlePlay} alt="Google Play" />
              <img src={appStore} alt="App Store" />
            </div>
          </div>
        </div>

        {/* Cột 2 */}
        <div className="footer__col">
          <h4>Newsletter</h4>
          <p className="footer__desc">
            It has a more-or-less normal distribution of letters, as opposed to using.
          </p>
          <div className="footer__subscribe">
            <input type="email" placeholder="Your Email Address" />
            <button><Send size={16} /></button>
          </div>
          <button className="footer__btn">SUBSCRIBE</button>
        </div>

        {/* Cột 3 */}
        <div className="footer__col">
          <h4>Official Info</h4>
          <ul className="footer__info">
            <li><Phone size={16} /> +9444454787212</li>
            <li><Mail size={16} /> yourmail.info.com</li>
            <li><MapPin size={16} /> 355Eligan South, California</li>
          </ul>
          <div className="footer__socials">
            <Facebook size={18} />
            <Linkedin size={18} />
            <Youtube size={18} />
            <Instagram size={18} />
          </div>
        </div>

        {/* Cột 4 */}
        <div className="footer__col">
          <h4>Quick Link</h4>
          <ul className="footer__links">
            <li>About Us</li>
            <li>Work Gallery</li>
            <li>Client Feedback</li>
            <li>Our Service</li>
            <li>Our Team</li>
            <li>Contact Us</li>
          </ul>
        </div>
      </div>

      <div className="footer__bottom">
        <p>© Tromar 2023 | Allright Reserved</p>
        <div className="footer__legal">
          <a href="#">Privacy</a>
          <a href="#">Terms</a>
          <a href="#">Sitemap</a>
          <a href="#">Help</a>
        </div>
      </div>
    </footer>
  );
}
