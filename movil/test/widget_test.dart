import 'package:flutter_test/flutter_test.dart';
import 'package:movil/main.dart';

void main() {
  testWidgets('Emergency dashboard renders and loads mock cases', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(const MyApp());

    expect(find.text('Atencion de Emergencias'), findsOneWidget);
    expect(find.text('Enviar alerta de emergencia'), findsOneWidget);

    await tester.pump(const Duration(milliseconds: 900));

    expect(find.text('CU-07'), findsOneWidget);
    expect(find.text('CU-11'), findsOneWidget);
  });
}
