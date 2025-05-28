import BookingSection from '../components/BookingSection';
import Footer from '../components/Footer';
import HeroSection from '../components/HeroSection';
import HomeAbout from '../components/HomeAbout';
import ServiceSection from '../components/ServiceSection';
import TaxiCollection from '../components/TaxiCollection';

export default function Home() {
  return (
    <div>
        <HeroSection />
        <HomeAbout />
        <ServiceSection />
        <BookingSection />
        <TaxiCollection />
    </div>
    
  );
}
