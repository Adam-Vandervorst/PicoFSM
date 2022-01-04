import scala.reflect.Typeable

type Transition[S, L] = PartialFunction[S, PartialFunction[L, S]]

extension [S, L](f: Transition[S, L])
  def both[S_, L_](g: Transition[S_, L_]): Transition[(S, S_), (L, L_)] =
    {case (f(m1), g(m2)) => {case (m1(b1), m2(b2)) => (b1, b2)}}

  def mixed[S_, L_](g: Transition[S_, L_]): Transition[(S, S_), (L, L_)] =
    {case (a1 @ f(m1), a2 @ g(m2)) => {case (m1(b1), m2(b2)) => (b1, b2)
                                       case (m1(b1), _) => (b1, a2)
                                       case (_, m2(b2)) => (a1, b2)}
     case (f(m1), a2) => {case (m1(b1), _) => (b1, a2)}
     case (a1, g(m2)) => {case (_, m2(b2)) => (a1, b2)}}

  def either[S_, L_](g: Transition[S_, L_]): Transition[(S, S_), Either[L, L_]] =
    {case (a1, a2) if f.isDefinedAt(a1) && g.isDefinedAt(a2) => ((el: Either[L, L_]) =>
      el.fold(f(a1).unapply(_).map((_, a2)), g(a2).unapply(_).map((a1, _)))).unlift}


class SM[S, L](val init: S, val adj: Transition[S, L]):
  private val path = collection.mutable.Stack[Either[S, L]](Left(init))

  def branch(): SM[S, L] =
    val fsm = SM(init, adj)
    fsm.path.addAll(path)
    fsm
  def state: S = path.collectFirst{case Left(s) => s}.get
  def accepts(l: L): Boolean = adj(state).isDefinedAt(l)
  def put(l: L): Boolean =
    path.prepend(Right(l))
    adj(state).unapply(l).map(s => path.prepend(Left(s))).nonEmpty

  def ⨯[S_, L_](other: SM[S_, L_]): SM[(S, S_), (L, L_)] =
    SM((this.init, other.init), this.adj both other.adj)
  def ☒[S_, L_](other: SM[S_, L_]): SM[(S, S_), (L, L_)] =
    SM((this.init, other.init), this.adj mixed other.adj)
  def +[S_, L_](other: SM[S_, L_]): SM[(S, S_), Either[L, L_]] =
    SM((this.init, other.init), this.adj either other.adj)
