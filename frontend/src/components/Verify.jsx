import { useState } from 'react';
import { Container, Form, Button, Alert, Card } from 'react-bootstrap';
import api from '../api/axiosConfig';
import { computeFileHash } from '../utils/crypto';

function Verify() {
    const [file, setFile] = useState(null);
    const [hash, setHash] = useState('');
    const [verifying, setVerifying] = useState(false);
    const [result, setResult] = useState(null);
    const [error, setError] = useState('');

    const handleFileChange = async (e) => {
        const selected = e.target.files[0];
        setFile(selected);
        if (selected) {
            const h = await computeFileHash(selected);
            setHash(h);
        } else {
            setHash('');
        }
    };

    const handleVerify = async () => {
        if (!file) return;
        setVerifying(true);
        setError('');
        setResult(null);

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await api.post('/api/timestamps/verify', formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });
            setResult(response.data);
        } catch (err) {
            setError(err.response?.data?.detail || 'Грешка при верификација');
        } finally {
            setVerifying(false);
        }
    };

    return (
        <Container className="mt-4">
            <h2>Верифицирај документ</h2>
            <Form>
                <Form.Group className="mb-3">
                    <Form.Label>Избери датотека</Form.Label>
                    <Form.Control type="file" onChange={handleFileChange} />
                </Form.Group>
                {hash && (
                    <Alert variant="info">
                        <strong>SHA-256 хаш:</strong> {hash}
                    </Alert>
                )}
                <Button
                    variant="success"
                    onClick={handleVerify}
                    disabled={!file || verifying}
                >
                    {verifying ? 'Верификација...' : 'Верифицирај'}
                </Button>
            </Form>
            {error && <Alert variant="danger" className="mt-3">{error}</Alert>}
            {result && (
                <Card className="mt-3">
                    <Card.Header>Резултат од верификација</Card.Header>
                    <Card.Body>
                        <Alert variant={result.verified ? 'success' : 'warning'}>
                            {result.verified ? '✅ Документот е автентичен' : '❌ Документот не е пронајден или не е автентичен'}
                        </Alert>
                        <pre>{JSON.stringify(result, null, 2)}</pre>
                    </Card.Body>
                </Card>
            )}
        </Container>
    );
}

export default Verify;