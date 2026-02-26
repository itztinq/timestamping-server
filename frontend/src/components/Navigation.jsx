import { Navbar, Nav, Container } from 'react-bootstrap';
import { Link, useNavigate } from 'react-router-dom';

function Navigation() {
    const navigate = useNavigate();
    const token = localStorage.getItem('token');
    const role = localStorage.getItem('role');

    const handleLogout = () => {
        localStorage.removeItem('token');
        localStorage.removeItem('role');
        navigate('/login');
    };

    return (
        <Navbar bg="dark" variant="dark" expand="lg">
            <Container>
                <Navbar.Brand as={Link} to="/">Timestamping Server</Navbar.Brand>
                <Navbar.Toggle aria-controls="basic-navbar-nav" />
                <Navbar.Collapse id="basic-navbar-nav">
                    <Nav className="me-auto">
                        {token && (
                            <>
                                <Nav.Link as={Link} to="/dashboard">Почетна</Nav.Link>
                                <Nav.Link as={Link} to="/upload">Прикачи</Nav.Link>
                                <Nav.Link as={Link} to="/verify">Верифицирај</Nav.Link>
                                {role === 'admin' ? (
                                    <Nav.Link as={Link} to="/all-timestamps">Сите записи</Nav.Link>
                                ) : (
                                    <Nav.Link as={Link} to="/timestamps">Мои записи</Nav.Link>
                                )}
                                <Nav.Link as={Link} to="/certificate">Сертификат</Nav.Link>
                            </>
                        )}
                    </Nav>
                    <Nav>
                        {token ? (
                            <Nav.Link onClick={handleLogout}>Одјави се</Nav.Link>
                        ) : (
                            <>
                                <Nav.Link as={Link} to="/login">Најава</Nav.Link>
                                <Nav.Link as={Link} to="/register">Регистрација</Nav.Link>
                            </>
                        )}
                    </Nav>
                </Navbar.Collapse>
            </Container>
        </Navbar>
    );
}

export default Navigation;