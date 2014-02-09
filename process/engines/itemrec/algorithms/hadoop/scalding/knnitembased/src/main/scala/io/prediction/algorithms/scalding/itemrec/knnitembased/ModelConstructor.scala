package io.prediction.algorithms.scalding.itemrec.knnitembased

import com.twitter.scalding._

import io.prediction.commons.filepath.{ DataFile, AlgoFile }
import io.prediction.commons.scalding.modeldata.ItemRecScores

/**
 * Source:
 *   selectedItems.tsv
 *   itemRecScores.tsv
 * Sink:
 *   itemRecScores DB
 * Description:
 *   Read the itemRecScores.tsv and get additional attributes from selectedItems.tsv for each similiar items.
 *   Then write the result to model DB.
 *
 * Required args:
 * --dbType: <string> modeldata DB type (eg. mongodb) (see --dbHost, --dbPort)
 * --dbName: <string> (eg. predictionio_modeldata)
 *
 * --hdfsRoot: <string>. Root directory of the HDFS
 *
 * --appid: <int>
 * --engineid: <int>
 * --algoid: <int>
 * --modelSet: <boolean> (true/false). flag to indicate which set
 * --recommendationTime: <long> (eg. 9876543210). recommend items with starttime <= recommendationTime and endtime > recommendationTime
 *
 * Optionsl args:
 * --dbHost: <string> (eg. "127.0.0.1")
 * --dbPort: <int> (eg. 27017)
 *
 * --evalid: <int>. Offline Evaluation if evalid is specified
 * --debug: <String>. "test" - for testing purpose
 *
 * Example:
 * batch:
 * scald.rb --hdfs-local io.prediction.algorithms.scalding.itemrec.knnitembased.ModelConstructor --dbType mongodb --dbName modeldata --dbHost 127.0.0.1 --dbPort 27017 --hdfsRoot hdfs/predictionio/ --appid 34 --engineid 3 --algoid 9 --modelSet false
 *
 * offline eval
 * scald.rb --hdfs-local io.prediction.algorithms.scalding.itemrec.knnitembased.ModelConstructor --dbType file --dbName modeldata_path/ --hdfsRoot hdfs/predictionio/ --appid 34 --engineid 3 --algoid 9 --modelSet false --evalid 15
 */
class ModelConstructor(args: Args) extends Job(args) {

  /**
   * parse args
   */
  val dbTypeArg = args("dbType")
  val dbNameArg = args("dbName")
  val dbHostArg = args.optional("dbHost")
  val dbPortArg = args.optional("dbPort") map (x => x.toInt)

  val hdfsRootArg = args("hdfsRoot")

  val appidArg = args("appid").toInt
  val engineidArg = args("engineid").toInt
  val algoidArg = args("algoid").toInt
  val evalidArg = args.optional("evalid") map (x => x.toInt)
  val OFFLINE_EVAL = (evalidArg != None) // offline eval mode

  val debugArg = args.list("debug")
  val DEBUG_TEST = debugArg.contains("test") // test mode

  val modelSetArg = args("modelSet").toBoolean
  val recommendationTimeArg = args("recommendationTime").toLong

  /**
   * input
   */
  val score = Tsv(AlgoFile(hdfsRootArg, appidArg, engineidArg, algoidArg, evalidArg, "itemRecScores.tsv")).read
    .mapTo((0, 1, 2) -> ('uid, 'iid, 'score)) { fields: (String, String, Double) => fields }

  val items = Tsv(DataFile(hdfsRootArg, appidArg, engineidArg, algoidArg, evalidArg, "selectedItems.tsv")).read
    .mapTo((0, 1, 2, 3) -> ('iidx, 'itypes, 'starttime, 'endtime)) { fields: (String, String, Long, String) =>
      val (iidx, itypes, starttime, endtime) = fields // itypes are comma-separated String

      val endtimeOpt: Option[Long] = endtime match {
        case "PIO_NONE" => None
        case x: String => {
          try {
            Some(x.toLong)
          } catch {
            case e: Exception => {
              assert(false, s"Failed to convert ${x} to Long. Exception: " + e)
              Some(0)
            }
          }
        }
      }

      (iidx, itypes.split(",").toList, starttime, endtimeOpt)
    }

  /**
   * process & output
   */
  val p = score.joinWithSmaller('iid -> 'iidx, items) // get items info for each iid
    .filter('starttime, 'endtime) { fields: (Long, Option[Long]) =>
      val (starttimeI, endtimeI) = fields

      val keepThis: Boolean = (starttimeI, endtimeI) match {
        case (start, None) => (recommendationTimeArg >= start)
        case (start, Some(end)) => ((recommendationTimeArg >= start) && (recommendationTimeArg < end))
        case _ => {
          assert(false, s"Unexpected item starttime ${starttimeI} and endtime ${endtimeI}")
          false
        }
      }
      keepThis
    }
    .project('uid, 'iid, 'score, 'itypes)
    .groupBy('uid) { _.sortBy('score).reverse.toList[(String, Double, List[String])](('iid, 'score, 'itypes) -> 'iidsList) }

  val src = ItemRecScores(dbType = dbTypeArg, dbName = dbNameArg, dbHost = dbHostArg, dbPort = dbPortArg, algoid = algoidArg, modelset = modelSetArg)

  p.then(src.writeData('uid, 'iidsList, algoidArg, modelSetArg) _)

}
