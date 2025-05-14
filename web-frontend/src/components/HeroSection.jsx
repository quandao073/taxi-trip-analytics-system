import '../css/Home/HeroSection.css';

export default function HeroSection() {
  return (
    <section className="hero">
      <div className="hero__overlay">
        <div className="hero__content">
          <p className="hero__tagline">GREAT EXPERIENCE IN BUILDING</p>
          <h1 className="hero__title">
            <span className='hero__title_1'>The best way to</span><br />
            <span className='hero__title_2'>Get around town.</span>
          </h1>
          <p className="hero__desc">
            Lorem ipsum dolor sit amet consectetur adipisicing elit. Quidem consequatur aspernatur deserunt neque provident maxime cum ipsa possimus odit necessitatibus cupiditate dolor rem, temporibus similique vitae porro, vero rerum corrupti?
          </p>
          <div className="hero__buttons">
            <button className="hero__btn hero__btn--primary">BOOK A TAXI</button>
            <button className="hero__btn hero__btn--outline">LEARN MORE</button>
          </div>
        </div>
      </div>
    </section>
  );
}
