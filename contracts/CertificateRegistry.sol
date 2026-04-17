// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title CertificateRegistry
 * @dev Blockchain-based Academic Certificate Verification System
 * @notice Issues and verifies tamper-proof academic certificates
 */
contract CertificateRegistry {

    address public admin;
    uint256 public totalIssued;
    uint256 public totalVerified;

    struct Certificate {
        string studentName;
        string rollNumber;
        string degree;
        string institution;
        uint256 issueDate;
        bool isValid;
        address issuedBy;
    }

    // certificateHash => Certificate
    mapping(bytes32 => Certificate) private certificates;

    // rollNumber => list of certificate hashes
    mapping(string => bytes32[]) private studentCertificates;

    // Events
    event CertificateIssued(
        bytes32 indexed certHash,
        string studentName,
        string rollNumber,
        string degree,
        uint256 issueDate
    );

    event CertificateRevoked(
        bytes32 indexed certHash,
        string reason
    );

    event CertificateVerified(
        bytes32 indexed certHash,
        string studentName,
        bool isValid
    );

    // Modifiers
    modifier onlyAdmin() {
        require(msg.sender == admin, "Only admin can perform this action");
        _;
    }

    modifier certExists(bytes32 _hash) {
        require(certificates[_hash].issueDate != 0, "Certificate does not exist");
        _;
    }

    constructor() {
        admin = msg.sender;
    }

    /**
     * @dev Issue a new certificate on the blockchain
     * @param _studentName Full name of the student
     * @param _rollNumber Unique roll/enrollment number
     * @param _degree Degree or course name
     * @param _institution Name of the issuing institution
     */
    function issueCertificate(
        string memory _studentName,
        string memory _rollNumber,
        string memory _degree,
        string memory _institution
    ) public onlyAdmin returns (bytes32) {

        // Generate unique hash from certificate data + timestamp
        bytes32 certHash = keccak256(
            abi.encodePacked(
                _studentName,
                _rollNumber,
                _degree,
                _institution,
                block.timestamp,
                block.number
            )
        );

        require(certificates[certHash].issueDate == 0, "Certificate already exists");

        certificates[certHash] = Certificate({
            studentName: _studentName,
            rollNumber: _rollNumber,
            degree: _degree,
            institution: _institution,
            issueDate: block.timestamp,
            isValid: true,
            issuedBy: msg.sender
        });

        studentCertificates[_rollNumber].push(certHash);
        totalIssued++;

        emit CertificateIssued(certHash, _studentName, _rollNumber, _degree, block.timestamp);

        return certHash;
    }

    /**
     * @dev Verify a certificate using its hash
     * @param _certHash The certificate hash to verify
     */
    function verifyCertificate(bytes32 _certHash)
        public
        certExists(_certHash)
        returns (bool, string memory, string memory, string memory, uint256)
    {
        Certificate memory cert = certificates[_certHash];
        totalVerified++;

        emit CertificateVerified(_certHash, cert.studentName, cert.isValid);

        return (
            cert.isValid,
            cert.studentName,
            cert.rollNumber,
            cert.degree,
            cert.issueDate
        );
    }

    /**
     * @dev Revoke a certificate (e.g., fraudulent submission)
     */
    function revokeCertificate(bytes32 _certHash, string memory _reason)
        public
        onlyAdmin
        certExists(_certHash)
    {
        certificates[_certHash].isValid = false;
        emit CertificateRevoked(_certHash, _reason);
    }

    /**
     * @dev Get certificate details (read-only)
     */
    function getCertificate(bytes32 _certHash)
        public
        view
        certExists(_certHash)
        returns (
            string memory studentName,
            string memory rollNumber,
            string memory degree,
            string memory institution,
            uint256 issueDate,
            bool isValid
        )
    {
        Certificate memory cert = certificates[_certHash];
        return (
            cert.studentName,
            cert.rollNumber,
            cert.degree,
            cert.institution,
            cert.issueDate,
            cert.isValid
        );
    }

    /**
     * @dev Get all certificate hashes for a student
     */
    function getStudentCertificates(string memory _rollNumber)
        public
        view
        returns (bytes32[] memory)
    {
        return studentCertificates[_rollNumber];
    }

    /**
     * @dev Transfer admin role
     */
    function transferAdmin(address _newAdmin) public onlyAdmin {
        require(_newAdmin != address(0), "Invalid address");
        admin = _newAdmin;
    }

    /**
     * @dev Get contract statistics
     */
    function getStats() public view returns (uint256 issued, uint256 verified) {
        return (totalIssued, totalVerified);
    }
}
