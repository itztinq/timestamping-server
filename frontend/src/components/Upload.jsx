import { useState } from 'react';
import { Container, Form, Button, Alert, Card } from 'react-bootstrap';
import api from '../api/axiosConfig';
import { computeFileHash } from '../utils/crypto';

function Upload() {
    const [file, setFile] = useState(null);
    const [hash, setHash] = useState('');
    const [uploading, setUploading] = useState(false);
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

    const handleUpload = async () => {
        if (!file) return;
        setUploading(true);
        setError('');
        setResult(null);

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await api.post('/api/timestamps/upload', formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });
            setResult(response.data);
        } catch (err) {
            setError(err.response?.data?.detail || 'Грешка при прикачување');
        } finally {
            setUploading(false);
        }
    };

    return (
        <Container className="mt-4">
            <h2>Прикачи документ за временски печат</h2>
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
                    variant="primary"
                    onClick={handleUpload}
                    disabled={!file || uploading}
                >
                    {uploading ? 'Прикачување...' : 'Прикачи'}
                </Button>
            </Form>
            {error && <Alert variant="danger" className="mt-3">{error}</Alert>}
            {result && (
                <Card className="mt-3">
                    <Card.Header>Резултат од прикачување</Card.Header>
                    <Card.Body>
                        <pre>{JSON.stringify(result, null, 2)}</pre>
                    </Card.Body>
                </Card>
            )}
        </Container>
    );
}

export default Upload;