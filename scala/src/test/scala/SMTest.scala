import org.scalatest.funsuite.AnyFunSuite


class SMTest extends AnyFunSuite:
  val sm1: SM[String, String] = SM("locked", Map(
    "locked" -> Map("unlock" -> "unlocked"),
    "unlocked" -> Map("lock" -> "locked", "open" -> "opened"),
    "opened" -> Map("close" -> "unlocked"),
  ))
  val sm2: SM[String, Int] = SM("a", Map(
    "a" -> Seq("b", "c"),
    "b" -> Seq("d"),
    "c" -> Seq("d"),
    "d" -> Seq("a", "e"),
    "e" -> Seq(),
    "f" -> Seq()
  ))
  val sm3: SM[Int, -1 | 0 | 1] = SM(0, i => d => i + d)
  val sm4: SM[Boolean, Boolean] = SM(false, x => y => x != y)
  val sm5: SM[String, Char] = SM("", s => {case c if !s.contains(c) => s :+ c})
  val sm6: SM[Set[Int], Int] = SM(Set(1, 2, 3), s => {case i if s.contains(i) => s - i})

  test("branch put state") {
    val f1 = sm1.branch()
    f1.put("unlock")
    assert(f1.state != sm1.state)
  }

  test("initial put state") {
    val (f1, f2, f6) = (sm1.branch(), sm2.branch(), sm6.branch())

    assert(!f1.put("random"))
    assert(f1.state == "locked")

    assert(!f2.put(2))
    assert(f2.state == "a")

    assert(!f6.put(4))
    assert(f6.state == Set(1, 2, 3))
  }

  test("tensor") {
    val f35 = sm3.branch() ⨯ sm5.branch()
    assert(f35.put((1, 'a')))
    assert(f35.state == (1, "a"))
    assert(f35.put((1, 'b')))
    assert(f35.state == (2, "ab"))
    assert(!f35.put((1, 'a')))
  }

  test("strong") {
    val f25 = sm2.branch() ☒ sm5.branch()
    assert(f25.put((2, 'a')))
    assert(f25.state == ("a", "a"))
    assert(f25.put((1, 'b')))
    assert(f25.state == ("c", "ab"))
    assert(f25.put((0, 'a')))
    assert(f25.state == ("d", "ab"))
    assert(!f25.put((2, 'a')))
  }

  test("sum") {
    val f12 = sm1.branch() + sm2.branch()
    assert(f12.put(Left("unlock")))
    assert(f12.state == ("unlocked", "a"))
    assert(!f12.put(Left("random")))
    assert(!f12.put(Right(2)))
    assert(f12.state == ("unlocked", "a"))
    assert(f12.put(Right(0)))
    assert(f12.put(Right(0)))
    assert(f12.put(Right(1)))
    assert(f12.state == ("unlocked", "e"))
    assert(!f12.put(Right(0)))
    assert(f12.put(Left("lock")))
    assert(f12.state == ("locked", "e"))
  }
