import { NavLink } from 'react-router-dom';
import { Search } from 'lucide-react';
import '../css/Header.css';

export default function Header() {

    return (
        <header className="header">
            <div className="header__container">
                <div className="header__logo">QuanDA</div>

                <nav className="header__nav">
                    <NavLink
                        to="/"
                        className={({ isActive }) => `header__link ${isActive ? 'header__link--active' : ''}`}>HOME</NavLink>
                    <NavLink
                        to="/dashboard"
                        className={({ isActive }) => `header__link ${isActive ? 'header__link--active' : ''}`}>STATISTICS</NavLink>
                    <NavLink
                        to="/"
                        className="header__link"
                        onClick={(e) => {
                            e.preventDefault();
                            const section = document.getElementById('services');
                            if (section) section.scrollIntoView({ behavior: 'smooth' });
                        }}
                    >
                        SERVICE
                    </NavLink>

                    <NavLink
                        to="/"
                        className="header__link"
                        onClick={(e) => {
                            e.preventDefault();
                            const section = document.getElementById('aboutus');
                            if (section) section.scrollIntoView({ behavior: 'smooth' });
                        }}
                    >
                        ABOUT US
                    </NavLink>
                    <NavLink
                        to="/"
                        className="header__link"
                        onClick={(e) => {
                            e.preventDefault();
                            const section = document.getElementById('contact');
                            if (section) section.scrollIntoView({ behavior: 'smooth' });
                        }}
                    >
                        CONTACT
                    </NavLink>

                </nav>

                <div className="header__actions">
                    <button className="header__icon-button" title="Tìm kiếm">
                        <Search size={24} />
                    </button>
                    <button className="header__signin-button">Sign in</button>
                </div>
            </div>
        </header>
    );
}
