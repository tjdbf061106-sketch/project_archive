"""
QSAR Report Generator
VEGA 스타일의 예측 리포트 생성
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
import io
from pathlib import Path
import numpy as np

from rdkit import Chem
from rdkit.Chem import Draw, AllChem, DataStructs
from rdkit.ML.Descriptors import MoleculeDescriptors

class QSARReportGenerator:
    """QSAR 예측 리포트 생성기"""

    def __init__(self, training_data_path=None):
        """
        Parameters:
        -----------
        training_data_path : str
            학습 데이터 경로 (Applicability Domain 계산용)
        """
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
        self.training_fingerprints = None
        self.training_smiles = None

        # 학습 데이터 로드 (있는 경우)
        if training_data_path:
            self._load_training_data(training_data_path)

    def _setup_custom_styles(self):
        """커스텀 스타일 설정"""
        # 제목 스타일
        if 'CustomTitle' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='CustomTitle',
                parent=self.styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#2c3e50'),
                spaceAfter=30,
                alignment=TA_CENTER,
                fontName='Helvetica-Bold'
            ))

        # 섹션 제목
        if 'SectionTitle' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='SectionTitle',
                parent=self.styles['Heading2'],
                fontSize=16,
                textColor=colors.HexColor('#34495e'),
                spaceAfter=12,
                spaceBefore=12,
                fontName='Helvetica-Bold',
                borderWidth=2,
                borderColor=colors.HexColor('#3498db'),
                borderPadding=5,
                backColor=colors.HexColor('#ecf0f1')
            ))

        # 본문
        if 'CustomBody' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='CustomBody',
                parent=self.styles['Normal'],
                fontSize=11,
                leading=14,
                spaceAfter=10
            ))

        # 경고
        if 'CustomWarning' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='CustomWarning',
                parent=self.styles['Normal'],
                fontSize=11,
                textColor=colors.HexColor('#e74c3c'),
                backColor=colors.HexColor('#fadbd8'),
                borderWidth=1,
                borderColor=colors.HexColor('#e74c3c'),
                borderPadding=10,
                spaceAfter=10
            ))

    def _load_training_data(self, data_path):
        """학습 데이터 로드 (Fingerprint 계산)"""
        # TODO: 실제 학습 데이터 로드 로직
        pass

    def calculate_applicability_domain(self, query_smiles, top_n=5):
        """
        Applicability Domain 계산
        - Tanimoto similarity 기반
        - 가장 유사한 학습 데이터 top N 반환

        Parameters:
        -----------
        query_smiles : str
            쿼리 분자 SMILES
        top_n : int
            반환할 유사 분자 개수

        Returns:
        --------
        dict
            similarity_score: 평균 유사도
            similar_compounds: 유사 화합물 리스트
            in_domain: AD 내부 여부
        """
        query_mol = Chem.MolFromSmiles(query_smiles)
        if query_mol is None:
            return None

        # ECFP4 fingerprint 계산
        query_fp = AllChem.GetMorganFingerprintAsBitVect(query_mol, 2, nBits=1024)

        # 예시 학습 데이터 (실제로는 저장된 데이터 사용)
        training_examples = [
            {'smiles': 'CCO', 'label': 'Non-irritant', 'id': 'TRAIN_001'},
            {'smiles': 'c1ccccc1', 'label': 'Irritant', 'id': 'TRAIN_002'},
            {'smiles': 'CC(C)O', 'label': 'Non-irritant', 'id': 'TRAIN_003'},
            {'smiles': 'CC(=O)O', 'label': 'Irritant', 'id': 'TRAIN_004'},
            {'smiles': 'Oc1ccccc1', 'label': 'Irritant', 'id': 'TRAIN_005'},
        ]

        # 유사도 계산
        similarities = []
        for example in training_examples:
            train_mol = Chem.MolFromSmiles(example['smiles'])
            if train_mol:
                train_fp = AllChem.GetMorganFingerprintAsBitVect(train_mol, 2, nBits=1024)
                similarity = DataStructs.TanimotoSimilarity(query_fp, train_fp)
                similarities.append({
                    'smiles': example['smiles'],
                    'similarity': similarity,
                    'label': example['label'],
                    'id': example['id']
                })

        # 정렬 및 top N 선택
        similarities.sort(key=lambda x: x['similarity'], reverse=True)
        top_similar = similarities[:top_n]

        # 평균 유사도
        avg_similarity = np.mean([s['similarity'] for s in top_similar])

        # AD 판단 (threshold = 0.7)
        ad_threshold = 0.7
        in_domain = avg_similarity >= ad_threshold

        return {
            'similarity_score': avg_similarity,
            'similar_compounds': top_similar,
            'in_domain': in_domain,
            'threshold': ad_threshold
        }

    def calculate_leverage(self, descriptors, training_descriptors):
        """
        Leverage (h*) 계산 - QMRF 기반
        h* = x^T (X^T X)^-1 x

        Parameters:
        -----------
        descriptors : array
            쿼리 분자 descriptor
        training_descriptors : array
            학습 데이터 descriptors

        Returns:
        --------
        dict
            leverage: h* 값
            warning_threshold: h* = 3p/n
            in_domain: 도메인 내부 여부
        """
        n, p = training_descriptors.shape

        try:
            # X^T X 계산
            XTX = np.dot(training_descriptors.T, training_descriptors)

            # (X^T X)^-1 계산
            XTX_inv = np.linalg.inv(XTX)

            # h* = x^T (X^T X)^-1 x
            leverage = np.dot(np.dot(descriptors, XTX_inv), descriptors.T)[0, 0]

            # Warning threshold
            h_star_threshold = 3 * p / n

            return {
                'leverage': float(leverage),
                'threshold': float(h_star_threshold),
                'in_domain': leverage <= h_star_threshold,
                'n_samples': n,
                'n_features': p
            }
        except Exception as e:
            return {
                'leverage': None,
                'threshold': None,
                'in_domain': None,
                'error': str(e)
            }

    def generate_report(self, prediction_data, output_path):
        """
        VEGA 스타일 리포트 생성

        Parameters:
        -----------
        prediction_data : dict
            - smiles: SMILES 코드
            - molecule_name: 분자 이름 (optional)
            - predictions: {'eye': {...}, 'skin': {...}}
            - descriptors: 계산된 descriptor
            - timestamp: 예측 시간
        output_path : str
            출력 PDF 경로
        """
        doc = SimpleDocTemplate(output_path, pagesize=A4,
                                topMargin=0.75*inch, bottomMargin=0.75*inch)

        story = []

        # ==================== 헤더 ====================
        story.append(self._create_header())
        story.append(Spacer(1, 0.3*inch))

        # ==================== 1. Prediction Summary ====================
        story.append(Paragraph("1. PREDICTION SUMMARY", self.styles['SectionTitle']))
        story.append(Spacer(1, 0.15*inch))

        # 분자 정보
        story.append(self._create_molecule_info(prediction_data))
        story.append(Spacer(1, 0.2*inch))

        # 예측 결과 테이블
        story.append(self._create_prediction_table(prediction_data))
        story.append(Spacer(1, 0.2*inch))

        # 모델 정보
        story.append(self._create_model_info())
        story.append(Spacer(1, 0.3*inch))

        # ==================== 2. Molecular Descriptors ====================
        story.append(PageBreak())
        story.append(Paragraph("2. MOLECULAR DESCRIPTORS", self.styles['SectionTitle']))
        story.append(Spacer(1, 0.15*inch))

        story.append(self._create_descriptors_table(prediction_data.get('descriptors', {})))
        story.append(Spacer(1, 0.3*inch))

        # ==================== 3. Applicability Domain ====================
        story.append(PageBreak())
        story.append(Paragraph("3. APPLICABILITY DOMAIN", self.styles['SectionTitle']))
        story.append(Spacer(1, 0.15*inch))

        # 3.1 Similarity-based AD
        story.append(Paragraph("3.1 Similarity-based Assessment", self.styles['Heading3']))
        story.append(Spacer(1, 0.1*inch))

        ad_data = self.calculate_applicability_domain(prediction_data['smiles'])
        story.append(self._create_similarity_section(ad_data))
        story.append(Spacer(1, 0.2*inch))

        # 3.2 Leverage-based AD (QMRF)
        story.append(Paragraph("3.2 Leverage-based Assessment (QMRF)", self.styles['Heading3']))
        story.append(Spacer(1, 0.1*inch))

        # 예시 학습 데이터 (실제로는 저장된 데이터 사용)
        training_desc = np.random.randn(100, 14)  # 100 samples, 14 features
        query_desc = np.array(prediction_data.get('descriptors_array', np.random.randn(1, 14)))

        leverage_data = self.calculate_leverage(query_desc, training_desc)
        story.append(self._create_leverage_section(leverage_data))
        story.append(Spacer(1, 0.3*inch))

        # ==================== 4. References ====================
        story.append(PageBreak())
        story.append(Paragraph("4. REFERENCES & DISCLAIMER", self.styles['SectionTitle']))
        story.append(Spacer(1, 0.15*inch))
        story.append(self._create_references())

        # PDF 생성
        doc.build(story)

    def _create_header(self):
        """리포트 헤더 생성"""
        # 로고 대신 텍스트 헤더
        title = Paragraph(
            "<b>QSAR Irritation Prediction Report</b><br/>"
            "<font size=10>Eye & Skin Irritation Toxicity Assessment</font>",
            self.styles['CustomTitle']
        )
        return title

    def _create_molecule_info(self, data):
        """분자 정보 섹션"""
        smiles = data.get('smiles', 'N/A')
        name = data.get('molecule_name', 'Unknown')
        timestamp = data.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

        # 분자 구조 이미지 생성
        mol = Chem.MolFromSmiles(smiles)
        img_data = None
        if mol:
            img = Draw.MolToImage(mol, size=(300, 300))
            buf = io.BytesIO()
            img.save(buf, format='PNG')
            buf.seek(0)
            img_data = Image(buf, width=2*inch, height=2*inch)

        # 정보 테이블
        info_data = [
            ['Compound Name:', name],
            ['SMILES:', smiles],
            ['Report Date:', timestamp],
        ]

        info_table = Table(info_data, colWidths=[1.5*inch, 4*inch])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))

        elements = [info_table]
        if img_data:
            elements.append(Spacer(1, 0.15*inch))
            elements.append(img_data)

        return Table([[e] for e in elements], colWidths=[6*inch])

    def _create_prediction_table(self, data):
        """예측 결과 테이블"""
        predictions = data.get('predictions', {})

        table_data = [
            ['Endpoint', 'Prediction', 'Probability', 'Confidence', 'Threshold']
        ]

        for endpoint, result in predictions.items():
            endpoint_name = 'Eye Irritation' if endpoint == 'eye' else 'Skin Irritation'
            prediction = result.get('prediction', 'N/A')
            probability = f"{result.get('probability', 0):.3f}"
            confidence = result.get('confidence', 'N/A')
            threshold = f"{result.get('threshold', 0):.2f}"

            # 색상 설정
            if prediction == 'Irritant':
                color = colors.HexColor('#e74c3c')
            else:
                color = colors.HexColor('#27ae60')

            table_data.append([
                endpoint_name,
                prediction,
                probability,
                confidence,
                threshold
            ])

        table = Table(table_data, colWidths=[1.5*inch, 1.2*inch, 1.2*inch, 1*inch, 1*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
        ]))

        return table

    def _create_model_info(self):
        """모델 정보"""
        info = [
            Paragraph("<b>Training Data:</b>", self.styles['CustomBody']),
            Paragraph("• Eye Irritation: NTP ICE In Vivo data (EPA classification)", self.styles['CustomBody']),
            Paragraph("• Skin Irritation: NTP ICE In Vivo data (EPA classification)", self.styles['CustomBody']),
            Spacer(1, 0.1*inch),
            Paragraph("<b>Models:</b>", self.styles['CustomBody']),
            Paragraph("• Eye: Gradient Boosting Classifier (ROC-AUC: 0.765, Sensitivity: 81.7%)", self.styles['CustomBody']),
            Paragraph("• Skin: Support Vector Machine - RBF kernel (ROC-AUC: 0.756, Sensitivity: 76.5%)", self.styles['CustomBody']),
        ]

        return Table([[i] for i in info], colWidths=[6*inch])

    def _create_descriptors_table(self, descriptors):
        """Descriptor 테이블"""
        if not descriptors:
            return Paragraph("No descriptor data available.", self.styles['CustomBody'])

        table_data = [['Descriptor', 'Value']]

        for desc_name, value in descriptors.items():
            if isinstance(value, float):
                value_str = f"{value:.3f}"
            else:
                value_str = str(value)
            table_data.append([desc_name, value_str])

        table = Table(table_data, colWidths=[3*inch, 2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
        ]))

        return table

    def _create_similarity_section(self, ad_data):
        """유사도 기반 AD 섹션"""
        if not ad_data:
            return Paragraph("No applicability domain data available.", self.styles['CustomBody'])

        # 요약
        avg_sim = ad_data['similarity_score']
        in_domain = ad_data['in_domain']
        threshold = ad_data['threshold']

        summary = Paragraph(
            f"<b>Average Similarity:</b> {avg_sim:.3f} (Threshold: {threshold})<br/>"
            f"<b>Status:</b> {'Inside Applicability Domain' if in_domain else 'Outside Applicability Domain'}",
            self.styles['CustomBody']
        )

        # 유사 화합물 테이블
        table_data = [['Training ID', 'SMILES', 'Similarity', 'Label']]

        for compound in ad_data['similar_compounds']:
            table_data.append([
                compound['id'],
                compound['smiles'],
                f"{compound['similarity']:.3f}",
                compound['label']
            ])

        table = Table(table_data, colWidths=[1.2*inch, 2*inch, 1*inch, 1.3*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
        ]))

        return Table([[summary], [Spacer(1, 0.15*inch)], [table]], colWidths=[6*inch])

    def _create_leverage_section(self, leverage_data):
        """Leverage 기반 AD 섹션"""
        if not leverage_data or leverage_data.get('leverage') is None:
            return Paragraph("Leverage calculation unavailable.", self.styles['CustomBody'])

        h_star = leverage_data['leverage']
        threshold = leverage_data['threshold']
        in_domain = leverage_data['in_domain']

        formula = Paragraph(
            "<b>QMRF Formula:</b><br/>"
            "h* = x<sup>T</sup> (X<sup>T</sup> X)<sup>-1</sup> x<br/>"
            f"Warning threshold: h* = 3p/n = {threshold:.4f}<br/>"
            f"(n = {leverage_data['n_samples']} samples, p = {leverage_data['n_features']} features)",
            self.styles['CustomBody']
        )

        result = Paragraph(
            f"<b>Calculated Leverage:</b> {h_star:.4f}<br/>"
            f"<b>Status:</b> {'Inside Applicability Domain' if in_domain else 'Outside Applicability Domain (WARNING)'}",
            self.styles['CustomBody']
        )

        if not in_domain:
            warning = Paragraph(
                "⚠ <b>WARNING:</b> The compound has high leverage (h* > 3p/n), "
                "indicating it is structurally different from the training set. "
                "Predictions should be used with caution.",
                self.styles['CustomWarning']
            )
            return Table([[formula], [Spacer(1, 0.1*inch)], [result], [Spacer(1, 0.1*inch)], [warning]], colWidths=[6*inch])

        return Table([[formula], [Spacer(1, 0.1*inch)], [result]], colWidths=[6*inch])

    def _create_references(self):
        """참고문헌 및 면책사항"""
        refs = [
            Paragraph("<b>References:</b>", self.styles['Heading3']),
            Paragraph("1. NTP Interagency Center for the Evaluation of Alternative Toxicological Methods (NICEATM)", self.styles['CustomBody']),
            Paragraph("2. EPA ECOTOX Database", self.styles['CustomBody']),
            Paragraph("3. QSAR Model Reporting Format (QMRF)", self.styles['CustomBody']),
            Spacer(1, 0.2*inch),
            Paragraph("<b>Disclaimer:</b>", self.styles['Heading3']),
            Paragraph(
                "This prediction is generated by QSAR models and should be used for screening purposes only. "
                "The predictions are based on in vivo data and do not replace experimental testing. "
                "Users should consider the applicability domain assessment when interpreting results. "
                "Predictions outside the applicability domain should be treated with caution.",
                self.styles['CustomWarning']
            ),
        ]

        return Table([[r] for r in refs], colWidths=[6*inch])


# 테스트 코드
if __name__ == '__main__':
    generator = QSARReportGenerator()

    # 예시 데이터
    test_data = {
        'smiles': 'CCO',
        'molecule_name': 'Ethanol',
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'predictions': {
            'eye': {
                'prediction': 'Non-irritant',
                'probability': 0.25,
                'confidence': 'High',
                'threshold': 0.32
            },
            'skin': {
                'prediction': 'Non-irritant',
                'probability': 0.30,
                'confidence': 'Medium',
                'threshold': 0.47
            }
        },
        'descriptors': {
            'MolWt': 46.069,
            'MolLogP': -0.031,
            'TPSA': 20.23,
            'NumHAcceptors': 1,
            'NumHDonors': 1,
            'NumRotatableBonds': 0,
            'NumAromaticRings': 0,
            'FractionCSP3': 0.667,
            'NumHeteroatoms': 1,
            'NumSaturatedRings': 0,
            'NumAliphaticRings': 0,
            'RingCount': 0,
            'HeavyAtomCount': 3,
            'Mixture': 0
        },
        'descriptors_array': np.array([[46.069, -0.031, 20.23, 1, 1, 0, 0, 0.667, 1, 0, 0, 0, 3, 0]])
    }

    generator.generate_report(test_data, 'test_report.pdf')
    print("Test report generated: test_report.pdf")
