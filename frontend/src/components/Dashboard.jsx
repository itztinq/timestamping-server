import { Container, Row, Col, Card } from 'react-bootstrap';
import { Link } from 'react-router-dom';

function Dashboard() {
    const username = localStorage.getItem('username') || 'Корисник';

    return (
        <Container className="mt-4">
            <h1>Добредојде, {username}!</h1>
            <Row className="mt-4">
                <Col md={4}>
                    <Card>
                        <Card.Body>
                            <Card.Title>Прикачи документ</Card.Title>
                            <Card.Text>
                                Креирај временски печат за нов документ.
                            </Card.Text>
                            <Link to="/upload" className="btn btn-primary">Прикачи</Link>
                        </Card.Body>
                    </Card>
                </Col>
                <Col md={4}>
                    <Card>
                        <Card.Body>
                            <Card.Title>Верифицирај документ</Card.Title>
                            <Card.Text>
                                Провери дали документ е архивиран и автентичен.
                            </Card.Text>
                            <Link to="/verify" className="btn btn-success">Верифицирај</Link>
                        </Card.Body>
                    </Card>
                </Col>
                <Col md={4}>
                    <Card>
                        <Card.Body>
                            <Card.Title>Мои записи</Card.Title>
                            <Card.Text>
                                Прегледај ги сите твои временски печати.
                            </Card.Text>
                            <Link to="/timestamps" className="btn btn-info">Прегледај</Link>
                        </Card.Body>
                    </Card>
                </Col>
            </Row>
        </Container>
    );
}

export default Dashboard;